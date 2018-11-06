import numpy as np
import cv2
import glob
import configparser
import json

#パラメータ######################

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

train = np.empty((0,3),int)
labels = np.empty((0),int)

for i in range(bConf.getint('CLASSES')):
    paths = glob.glob("images/box2/class" + str(i+1) + "/*.jpg")

    for path in paths:
      img = cv2.imread(path)
      img = cv2.resize(img,(WIDTH,HEIGHT))
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
      
      m = cv2.moments(box, False)#障害物のモーメント
      mx,my = int(m["m10"]/m["m00"]) , int(m["m01"]/m["m00"])#重心の座標
      train = np.append(train, np.array([[m["m00"] / (10 ** 5), mx, my]]), axis=0)
      print(np.array([[m["m00"] / (10 ** 5), mx, my]]))

      labels = np.append(labels, i+1)

      if DEBUG is True:
        cv2.imshow('h',h)
        cv2.imshow('s',s)
        cv2.imshow('v',v)
        cv2.imshow('box',box)
        cv2.waitKey(0)

np.savez('box_data.npz',train=train, train_labels=labels)#モデル保存
