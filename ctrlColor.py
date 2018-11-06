import cv2
import numpy as np
import configparser
import json
import io
import base64
import png
import picamera

config  = configparser.ConfigParser()
config.read('config.ini')
gConf  = config['GENERAL']
WIDTH  = gConf.getint('WIDTH')
HEIGHT = gConf.getint('HEIGHT')

stream = io.BytesIO()
with picamera.PiCamera() as camera:
  camera.resolution = (WIDTH, HEIGHT)

def search(color, min,max):
  with picamera.PiCamera() as camera:
    camera.capture(stream, format='jpeg')
  bindata = np.fromstring(stream.getvalue(), dtype=np.uint8)
  img = cv2.imdecode(bindata, 1)
  hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  hsv = {
    'h': 0,
    's': 1,
    'v': 2
  }
  index = hsv[color]

  e = hsvImg[:,:, index]
  colorMask = np.zeros(e.shape,dtype='uint8')
  colorRange = (e >= min) & ( e <= max)
  colorMask[colorRange] = 255
  box = np.zeros(e.shape, dtype=np.uint8)
  box = cv2.add(box,colorMask)
  image = png.from_array(box, 'L')
  image.save(color + '.png')
  return image
  
