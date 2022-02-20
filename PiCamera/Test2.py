from picamera import PiCamera
from pathlib import Path
from time import sleep
from orbit import ISS
from skyfield.api import load
def snapshot():
  camera = PiCamera()
  base_folder = Path(__file__).parent.resolve()
  #camera.start_preview() for monitor
  for i in range(5):#in 3 hours the camera will take maximum 180 pics, 1 pic/min, I think we should count the 5s preview
    sleep(5)
    camera.capture('/home/pi/image%s.jpg' % i)
    location = ISS.coordinates()
    #camera.annotate_text = "Hello world!" maybe we can use this to mention the location of the ISS when the pic was taken
  #camera.stop_preview() preview works just for a monitor
  camera.close()
