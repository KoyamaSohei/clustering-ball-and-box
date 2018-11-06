import cv2
import numpy as np
import configparser
import json
import io
import picamera

#パラメータ######################

path = 'images/test/img-7.jpg'

config  = configparser.ConfigParser()
config.read('config.ini')
config.read('color.ini')

gConf  = config['GENERAL']
WIDTH  = gConf.getint('WIDTH')
HEIGHT = gConf.getint('HEIGHT')
DEBUG  = gConf.getboolean('DEBUG')

bConf  = config['BALL']
orange = config['ORANGE']
K      = bConf.getint('K')

################################

with np.load('ball_data.npz') as data:
  train = data['train']
  labels = data['train_labels']

knn = cv2.ml.KNearest_create()
knn.train(train.astype(np.float32), cv2.ml.ROW_SAMPLE, labels)

#img = cv2.imread(path)
#img = cv2.resize(img,(WIDTH,HEIGHT))

stream = io.BytesIO()
with picamera.PiCamera() as camera:
  camera.resolution = (WIDTH, HEIGHT)
  camera.capture(stream, format='jpeg')
bindata = np.fromstring(stream.getvalue(), dtype=np.uint8)
img = cv2.imdecode(bindata, 1)

hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

h = hsvImg[:, :, 0]
s = hsvImg[:, :, 1]
v = hsvImg[:, :, 2]

ball = np.zeros(h.shape, dtype=np.uint8)

orangeMask = np.zeros(h.shape,dtype='uint8')
t = json.loads(orange.get('threshold'))
orangeRange =  (h >= t[0]) & (h <= t[1]) & (s >= t[2]) & (s <= t[3]) & (v >= t[4]) & (v <= t[5])
orangeMask[orangeRange] = 255

ball = cv2.add(ball, orangeMask)


ret,thresh = cv2.threshold(ball,127,255,0)
image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

ballClasses = []
try:
    for cnt in contours:
        m = cv2.moments(cnt)
        if m["m00"] > 10 ** 2:
          mx,my = int(m["m10"]/m["m00"]) , int(m["m01"]/m["m00"])#重心の座標

          test = np.array([ mx, my])
          test = test.reshape(-1,2)
          ret,result,neighbours,dist = knn.findNearest(test.astype(np.float32),k=K)

          ballClasses.append(int(result[0][0]))#クラス番号           
except: 
  print('ball not found')

ballClasses = sorted(list(set(ballClasses)))
print(ballClasses)

if DEBUG is True:
  cv2.imshow('img',img)
  cv2.imshow('h',h)
  cv2.imshow('s',s)
  cv2.imshow('v',v)
  cv2.imshow('ball',ball)
  cv2.waitKey(0)
