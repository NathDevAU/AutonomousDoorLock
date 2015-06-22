#!/usr/bin/python

import cv2
import time
import sys

num_faces = 0
face_cascade=None
xLow = 300
xHigh = 380
yLow = 230
yHigh = 305

def face_detect(img, folder):
    global num_faces
    global face_cascade
    if face_cascade is None:
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    bwImg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(bwImg, 1.3, 5)
    for (x,y,w,h) in faces:
        print "face found!"
        tmp = img[y:y+h,x:x+w]
        cv2.imwrite("%s/face_%d.png" % (folder, num_faces), tmp)
        num_faces = num_faces + 1
    return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "USAGE: collect_face.py </path/to/save/images>"
        sys.exit()
    capture = cv2.VideoCapture(0)
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640); 
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480);
    while True:
        try:
            rc,img = capture.read()
            if not rc:
                continue
            img = img[yLow:yHigh,xLow:xHigh]
            face_detect(img, sys.argv[1])
            time.sleep(0.01)
        except KeyboardInterrupt:
            break
