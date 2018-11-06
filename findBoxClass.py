import numpy as np
import cv2
import configparser
import json
import io
import picamera

#パラメータ######################
path = 'images/box2/class3/01.jpg'#分類する画像のパス

config = configparser.ConfigParser()
config.read('config.ini')
config.read('color.ini')

gConf  = config['GENERAL']
WIDTH  = gConf.getint('WIDTH')
HEIGHT = gConf.getint('HEIGHT')
DEBUG  = gConf.getboolean('DEBUG')

bConf  = config['BOX']
K      = bConf.getint('K')

yellow = config['YELLOW']


################################

with np.load('box_data.npz') as data:
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

hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h = hsvImg[:, :, 0]
s = hsvImg[:, :, 1]
v = hsvImg[:, :, 2]
yellowMask = np.zeros(h.shape,dtype='uint8')
t = json.loads(yellow.get('threshold'))
yellowRange = (h >= t[0]) & (h <= t[1]) & (s >= t[2]) & (s <= t[3]) & (v >= t[4]) & (v <= t[5])
yellowMask[yellowRange] = 255
box = np.zeros(h.shape, dtype=np.uint8)
box = cv2.add(box, yellowMask)
      
ret,thresh = cv2.threshold(box,127,255,0)
image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

boxClasses = []
try:
  for cnt in contours:
    m = cv2.moments(cnt)#障害物のモーメント
    print(m["m00"])
    if m["m00"] > 20000:
      mx,my = int(m["m10"]/m["m00"]) , int(m["m01"]/m["m00"])#重心の座標

      test = np.array([m["m00"] / (10 ** 5), mx, my])
      
      test = test.reshape(-1,3)

      ret,result,neighbours,dist = knn.findNearest(test.astype(np.float32),k=K)

      boxClasses.append(int(result[0][0]))#クラス番号
except:
  print('box not found ')

print(boxClasses)


if DEBUG:
  cv2.imshow('h',h)
  cv2.imshow('s',s)
  cv2.imshow('v',v)
  cv2.imshow('detected circles',box)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
