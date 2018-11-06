import cv2
import numpy as np
import configparser
import json
import glob

config = configparser.ConfigParser()
config.read('config.ini')
config.read('color.ini')
gConf = config['GENERAL']
WIDTH,HEIGHT = gConf.getint('WIDTH'),gConf.getint('HEIGHT')
DEBUG = gConf.getboolean('DEBUG')
bConf = config['BALL']
orange = config['ORANGE']

train = np.empty((0,2),int)
labels = np.empty((0),int)

for i in range(bConf.getint('CLASSES')):

  paths = glob.glob("images/ball/class" + str(i+1) + "/*.jpg")

  for path in paths:
    img = cv2.imread(path)
    img = cv2.resize(img,(WIDTH,HEIGHT))
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

    m = cv2.moments(ball, False)
    mx,my = int(m["m10"]/m["m00"]) , int(m["m01"]/m["m00"])#重心の座標

    train = np.append(train, np.array([[ mx, my]]), axis=0)
    print(np.array([mx, my]))
    labels = np.append(labels, i+1)
    if DEBUG is True:
      cv2.imshow('h',h)
      cv2.imshow('s',s)
      cv2.imshow('v',v)
      cv2.imshow('ball',ball)
      cv2.waitKey(0)

np.savez('ball_data.npz',train=train, train_labels=labels)#モデル保存
