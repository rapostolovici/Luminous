from Test2_2 import snapshot
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
def convert(angle):
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle

def capture(camera, image):
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
def snapshot(index,camera):
  base_folder = Path(__file__).parent.resolve()#i think we can use this to identify the 'parent' folder in which we will save the images
  #camera.start_preview() for monitor
  #for i in range(5):#in 3 hours the camera will take maximum 180 pics, 1 pic/min, I think we should count the 5s preview
  sleep(5)
  #camera.capture('/home/pi/image%s.jpg' % i)
  image=capture(camera, f"{base_folder}/image%s.jpg" % index)
  return image
def clasify(image_file, data_file):
    script_dir = Path(__file__).parent.resolve()

    model_file = script_dir/'models/astropi-earth-water-clouds.tflite'
    data_dir = script_dir/'Data'
    label_file = data_dir/'earth-water-clouds.txt'
    #image_file = data_dir/'tests'/'photo_04415_51846074449_o.jpg'
interpreter = make_interpreter(f"{model_file}")
    interpreter.allocate_tensors()
    size = common.input_size(interpreter)
    image = Image.open(image_file).convert('RGB').resize(size, Image.ANTIALIAS)

    common.set_input(interpreter, image)
    interpreter.invoke()
    classes = classify.get_classes(interpreter, top_k=1)
labels = read_label_file(label_file)
    
    for c in classes:
        print(f'{labels.get(c.id, c.id)} {c.score:.5f}')
        row = (datetime.now(),image_file, f'{labels.get(c.id, c.id)}', f'{c.score:.5f}')
        add_csv_data(data_file, row)
def create_csv(data_file):
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Date/time", "Image", "Label", "Score")
        writer.writerow(header)
def add_csv_data(data_file, data):
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
    clasify(image, data_file)
    #sleep(1)
    # Update the current time
    now_time = datetime.now() 
  except Exception as e:
    logger.error(f'{e.__class__.__name__}: {e})')
camera.close()
