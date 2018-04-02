import cv2
from functools import wraps
from pygame import mixer
import time
from playsound import playsound

lastsave = 0


def counter(func):
    @wraps(func)
    def tmp(*args, **kwargs):
        tmp.count += 1
        global lastsave
        if time.time() - lastsave > 3:
            # this is in seconds, so 5 minutes = 300 seconds
            lastsave = time.time()
            tmp.count = 0
        return func(*args, **kwargs)
    tmp.count = 0
    return tmp




#cap = cv2.VideoCapture(0)


@counter
def closed():
  print ("Eye Closed")


def openeye():
  print ("Eye is Open")
face_cascade=None
eye_cascade=None
def load():
    global face_cascade,eye_cascade 
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

def sound():
    playsound("alarm.mp3")

def pre(img):
    global face_cascade,eye_cascade
    load() 
    if 1:
        #ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            if eyes is not ():
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    openeye()
            else:
               closed()
               if closed.count == 3:
                   print ("driver is sleeping")
                   playsound("alarm.mp3")

        cv2.imshow('img', img)
        k = cv2.waitKey(30) & 0xff

