from picamera import PiCamera
from pathlib import Path
from time import sleep
from orbit import ISS
from skyfield.api import load
def convert(angle):
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle

def capture(camera, image):
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
def snapshot():

  camera = PiCamera()
  base_folder = Path(__file__).parent.resolve()#i think we can use this to identify the 'parent' folder in which we will save the images
  #camera.start_preview() for monitor
  for i in range(5):#in 3 hours the camera will take maximum 180 pics, 1 pic/min, I think we should count the 5s preview
    sleep(5)
    #camera.capture('/home/pi/image%s.jpg' % i)
    capture(camera, f"{base_folder}/image%s.jpg' % i")
    #camera.annotate_text = "Hello world!" maybe we can use this to mention the location of the ISS when the pic was taken
  #camera.stop_preview() preview works just for a monitor
  camera.close()
