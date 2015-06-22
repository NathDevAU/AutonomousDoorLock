#!/usr/bin/python

import cv2
import time
import sys
import numpy as np

xLow = 300
xHigh = 380
yLow = 230
yHigh = 305

capture = cv2.VideoCapture(0)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640) 
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
if len(sys.argv) < 2:
    template = cv2.imread("background.png")
    while True:
        rc,img = capture.read()
        if not rc:
            continue
        img = img[yLow:yHigh,xLow:xHigh]
        total = cv2.sumElems(cv2.sumElems(cv2.subtract(img,template)))
        print "Total: " + str(total[0])
else:
    rc,img = capture.read()
    while not rc:
        rc,img = capture.read()

    img = img[yLow:yHigh,xLow:xHigh]
    cv2.imwrite("background.png", img)
