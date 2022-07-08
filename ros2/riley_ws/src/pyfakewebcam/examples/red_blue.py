import time
import pyfakewebcam
import numpy as np

blue = np.zeros((720,1280,3), dtype=np.uint8)
blue[:,:,2] = 255

red = np.zeros((720,1280,3), dtype=np.uint8)
red[:,:,0] = 255

camera = pyfakewebcam.FakeWebcam('/dev/video1', 1280, 720)

while True:

    camera.schedule_frame(red)
    time.sleep(1/30.0)

    camera.schedule_frame(blue)
    time.sleep(1/30.0)
