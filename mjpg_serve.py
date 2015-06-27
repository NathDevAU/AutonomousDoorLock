#!/usr/bin/python

#Copyright Steven Hickson
#Heavily modified httpserver script from Igor Maculan

import cv2
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import time
from threading import Thread, Lock
import numpy as np
from RPIO import PWM

capture=None
result=None
face_cascade=None
face_model=None
template=None
mutex = Lock()
servo = PWM.Servo()
restartCount = 30

xLow = 300
xHigh = 380
yLow = 230
yHigh = 305
faceConf = 475
openThresh = 150000
closeThresh = 90000
isOpen = False
locked = True

def lock():
    #lock
    global locked
    locked = True
    print "locking!"
    servo.set_servo(18, 2000)
    time.sleep(0.5)
    servo.stop_servo(18)
    return

def unlock():
    #unlock
    global locked
    locked = False
    print "unlocking!"
    servo.set_servo(18, 1200)
    time.sleep(0.4)
    servo.stop_servo(18)
    return

def isDoorOpen(img):
    global template
    global isOpen
    global openThresh
    global closeThresh
    tmp = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    tmp[:,:,2] = 0
    total = cv2.sumElems(cv2.sumElems(cv2.absdiff(tmp,template)))
    #print "Total: " + str(total[0])
    if total[0] > openThresh:
        #print "Open"
        isOpen = True
        return True
    #print "Closed"
    if total[0] <= closeThresh:
        isOpen = False
        return False
    return isOpen

def face_detect(img):
    global face_cascade
    global face_model
    global restartCount
    global locked
    if face_cascade is None:
        face_cascade = cv2.CascadeClassifier('/home/pi/RPi_Ipcam/haarcascade_frontalface_default.xml')
    if face_model is None:
        face_model = cv2.createEigenFaceRecognizer()
        face_model.load("/home/pi/RPi_Ipcam/model.xml")
    #check if door is open
    isOpen = isDoorOpen(img)
    if isOpen:
        locked = False
        #print "unlocked"
    #else:
        #print "locked"
    if not locked and not isOpen:
        lock()
        #print "locked"
    #check for faces
    bwImg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(bwImg, 1.1, 1)
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x + w, y + h), (255,0,0), 2)
        #gray = cv2.cvtColor(img[y:y+h,x:x+w], cv2.COLOR_BGR2GRAY)
        [p_label, p_confidence] = face_model.predict(np.asarray(cv2.resize(bwImg, (42,42))))
        # Print it:
        print "Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence)
        if p_confidence < 499:
            unlock()
            time.sleep(2)
            #lock()
            restartCount = 0
            #print "face_detect: restartCount = " + str(restartCount)
    return img

def img_thread():
    global result
    global xLow
    global xHigh
    global yLow
    global yHigh
    global mutex
    while True:
        try:
            rc,img = capture.read()
            if not rc:
                result = None
                continue
            img = img[yLow:yHigh,xLow:xHigh]
            mutex.acquire()
            result = img
            mutex.release()
            time.sleep(0.25)
        except KeyboardInterrupt:
            break
    return

def process_thread():
    global result
    global restartCount
    global mutex
    while True:
        try:
            if result != None:
                if restartCount > 30:
                    mutex.acquire()
                    result = face_detect(result)
                    mutex.release()
                else:
                    restartCount = restartCount + 1
                    #print "ProcessThread: restartCount = " + str(restartCount)
                    time.sleep(0.25)
            time.sleep(0.05)
        except KeyboardInterrupt:
            break
    return

class CamHandler(BaseHTTPRequestHandler):
    global result
    def do_GET(self):
        print self.path
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    if result != None:
                        r, buf = cv2.imencode(".jpg",result)
                        self.wfile.write("--jpgboundary\r\n")
                        self.send_header('Content-type','image/jpeg')
                        self.send_header('Content-length',str(len(buf)))
                        self.end_headers()
                        self.wfile.write(bytearray(buf))
                        self.wfile.write('\r\n')
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html') or self.path=="/":
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="./cam.mjpg" />')
            self.wfile.write('</body></html>')
            return

def main():
    global capture
    global template
    capture = cv2.VideoCapture(0)
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640); 
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480);
    template = cv2.imread("/home/pi/RPi_Ipcam/background.png")
    template = cv2.cvtColor(template, cv2.COLOR_RGB2HSV)
    template[:,:,2] = 0
    lock()
    try:
        thread = Thread(target = img_thread)
        thread.daemon = True
        thread.start()
        thread2 = Thread(target = process_thread)
        thread2.daemon = True
        thread2.start()
        server = HTTPServer(('',8080),CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()

if __name__ == '__main__':
    main()

