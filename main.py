
from datetime import datetime, timedelta
from logzero import logger, logfile
from pathlib import Path
from time import sleep
from PIL import Image
from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from picamera import PiCamera
from orbit import ISS
from skyfield.api import load
import csv

#function to convert coordinates
def convert(angle):
    logger.info("Displaying the coordinates")
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle
    
#function to capture an image and add EXIF data with ISS coordinates
def capture(camera, image):
    logger.info("Taking a picture and finding the location of the ISS")
    """Use `camera` to capture an `image` file with lat/long EXIF data."""
    point = ISS.coordinates()
    # Convert the latitude and longitude to EXIF-appropriate representations
    south, exif_latitude = convert(point.latitude)
    west, exif_longitude = convert(point.longitude)
    # Set the EXIF tags specifying the current location
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"
    camera.capture(image)
    return image
    
#function to take an image and to save it
def snapshot(index,camera):
  logger.info("Saving the image")
  base_folder = Path(__file__).parent.resolve()
  sleep(15)
  image=capture(camera, f"{base_folder}/image%s.jpg" % index)
  return image

#function to classify an image 
def clasify(image_file,data_file):
    logger.info("classifying image")
    script_dir = Path(__file__).parent.resolve()
    model_file = script_dir/'models/astropi-earth-water-clouds.tflite'
    data_dir = script_dir/'Data'
    label_file = data_dir/'earth-water-clouds.txt'
    interpreter = make_interpreter(f"{model_file}")
    interpreter.allocate_tensors()
    size = common.input_size(interpreter)
    image = Image.open(image_file).convert('RGB').resize(size, Image.ANTIALIAS)
    common.set_input(interpreter, image)
    interpreter.invoke()
    classes = classify.get_classes(interpreter, top_k=1)
    labels = read_label_file(label_file)
    for c in classes:
        logger.info(f'{labels.get(c.id, c.id)} {c.score:.5f}')
        row = (datetime.now(),image_file, f'{labels.get(c.id, c.id)}', f'{c.score:.5f}')
        add_csv_data(data_file, row)

#function to create a csv file
def create_csv(data_file):
    logger.info("Creating a csv file")
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Date/time", "Image", "Label", "Score")
        writer.writerow(header)

#function to add the data in the csv file
def add_csv_data(data_file, data):
    logger.info("Adding the data to the csv file")
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
        
base_folder = Path(__file__).parent.resolve()
data_file = base_folder/'data.csv'
logfile(base_folder/"events.log")
# Create a `datetime` variable to store the start time
start_time = datetime.now()
# Create a `datetime` variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
# Run a loop for 168 minutes
running_time = 168
index = 0
camera = PiCamera()
camera.resolution = (2592,1944)
create_csv(data_file)

while (now_time < start_time + timedelta(minutes=running_time)):
  try:
    index+=1
    image = snapshot(index, camera)
    clasify(image,data_file)
    # Update the current time
    now_time = datetime.now() 
  except Exception as e:
    logger.error(f'{e.__class__.__name__}: {e})')
camera.close()