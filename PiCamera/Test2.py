from picamera import PiCamera
def snapshot():
  camera = PiCamera()
  camera.start_preview()
  sleep(5)
  camera.capture('home/pi/pic_1.png')
  camera.stop_preview()
  #camera.close()
