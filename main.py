import pygame
import sys
#50 line
import geocoder
from math import *
import pyowm

import cv2
import datetime
import numpy as np

import time
import threading
import json
from urllib.request import urlopen

from goompy import GooMPy
from PIL import ImageTk

from darkflow.net.build import TFNet
from yolov2 import run,predicty

from playsound import playsound

pygame.init()

options = {
    'model':'cfg/tiny-yolo.cfg',
    'load':'bin/tiny-yolo.weights',
    'threshold': 0.35,

}

black = (51, 51, 51)

videoFeed = cv2.VideoCapture(0)
vWidth = int(640*.7) - 5# 320
vHeight = int(480*.7) - 5# 240

width = 1200
height = 680
closestLabel = None
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

city = "OFFLINE"
mapCurr = None

mapW, mapH = 430, 260
lang=0
results=[]
frame=None
done=False
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]
class camera(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      #print("Starting " + self.name)
      get_frame(self.name)
      #print("Exiting " + self.name)

def get_frame(threadName):
    global frame,done,cap
    while not done:
        _, frame = cap.read()

class predictclass(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      #print("Starting " + self.name)
      predict(self.name)
      #print("Exiting " + self.name)

def predict(threadName):
    global results,frame,done
    while not done:
        results = tfnet.return_predict(frame)


#output_frame = OutputFrame()
webcam_thread = camera("camera thread")
predictor_thread = predictclass("predictclass thread")
webcam_thread.start()
time.sleep(1)
predictor_thread.start()


vehicles = ['car','motercycle','truck','bus']

def close():
    pygame.quit()
    sys.exit()
    videoFeed.release()
    cv2.destroyAllWindows()

def drawBackground(x, y, w, h):
    pygame.draw.rect(display, (63, 63, 63), (x, y, w, h))
    pygame.draw.rect(display, (65, 113, 156), (x, y, w, h), 1)

def getLatLan():
    try:
        g = geocoder.ip('me')
        val = g.latlng
        return val[0], val[1]
    except Exception as e:
        return None, None

def getCity():
    global city
    g = geocoder.ip('me')
    city = g.city


def weather():
    lat, lan = getLatLan()
    if not lat:
        return 0, 0, 0, "- -"
    else:
        owm = pyowm.OWM('ENTER KEY HERE')
        observation = owm.weather_at_coords(lat, lan)
        w = observation.get_weather()
        tmp = w.get_temperature('celsius')
        return tmp['temp'], w.get_humidity(), w.get_wind()['speed'], w.get_status()

def rotate(coord, angle, anchor=(0, 0)):
    #corr = 270
    return ((coord[0] - anchor[0])*cos(angle) - (coord[1] - anchor[1])*sin(angle),
            (coord[0] - anchor[0])*sin(angle) + (coord[1] - anchor[1])*cos(angle))

def translate(x, y, coord):
    return [coord[0] + x, coord[1] + y]

def getMonth(mon):
    if mon == 1:
        return "Jan"
    if mon == 2:
        return "Feb"
    if mon == 3:
        return "March"
    if mon == 4:
        return "April"
    if mon == 5:
        return "May"
    if mon == 6:
        return "Jun"
    if mon == 7:
        return "July"
    if mon == 8:
        return "Aug"
    if mon == 9:
        return "Sept"
    if mon == 10:
        return "Oct"
    if mon == 11:
        return "Nov"
    if mon == 12:
        return "Dec"

def getWeekDate(now):
    date = datetime.date(now.year, now.month, now.day)
    weekDay = date.isoweekday()
    day = 0
    if weekDay == 1:
        day = "Monday"
    if weekDay == 2:
        day = "Tuesday"
    if weekDay == 3:
        day = "Wednesday"
    if weekDay == 4:
        day = "Thursday"
    if weekDay == 5:
        day = "Friday"
    if weekDay == 6:
        day = "Saturday"
    if weekDay == 7:
        day = "Sunday"

    date = str(now.day) + " " + str(getMonth(now.month)) + " " + str(now.year)

    return date, day

def getMap():
    global mapCurr

    mapOffline = pygame.image.load("icons/offline.jpg")

    lat, lan = getLatLan()
    if not lat:
        lat = 0
        lan = 0
    try:
        goompy = GooMPy(mapW, mapH, lat, lan, 20, 'roadmap')
        image = goompy.getImage()

        mapCurr = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    except Exception as e:
        mapCurr = mapOffline
class Button:
    def __init__(self, x, y, w, h, action=None, shape="rect", origin="normal"):
        self.x = x
        self.y = y
        self.w = wplaysound
        self.h = h
        self.color = black
        self.activeColor = black
        self.action = action

        self.fontColor = None
        self.text = []
        self.font = None
        self.shape = shape

        self.image = None
        self.imagePos = None

        self.origin = origin

    def addText(self, text, pos, fontColor=black, size=15, font="Times New Roman", char="\n", align="centre"):
        self.fontColor = fontColor
        text = text.split(char)
        self.font = pygame.font.SysFont(str(font), size)

        if self.origin == "centre":
            x = self.x - self.w/2
            y = self.y - self.h/2
        else:
            x = self.x
            y = self.y

        for sent in text:
            textSurface, textPos = textObj(sent, self.font, self.fontColor)
            if align == "centre":
                textPos.center = (x +self.w/2+ pos[0], y +self.h/2+ pos[1] + len(self.text)*size)
            elif align == "left":
                textPos = (x + pos[0], y + pos[1] + len(self.text)*size)
            self.text.append([textSurface, textPos])

    def draw(self):
        pos = pygame.mouse.get_pos()
        if self.origin == "centre":
            x = self.x - self.w/2
            y = self.y - self.h/2
        else:
            x = self.x
            y = self.y

        if x <= pos[0] <= x + self.w and y <= pos[1] <= y + self.h:
            color = self.activeColor
        else:
            color = self.color

        if self.shape == "ellipse":
            pygame.draw.ellipse(display, color, (x, y, self.w, self.h))
        else:
            pygame.draw.rect(display, color, (x, y, self.w, self.h))
        if not (self.font == None):
            for sent in self.text:
                display.blit(sent[0], sent[1])
        if not (self.image == None):
            display.blit(self.image, self.imagePos)

    def isActive(self):
        pos = pygame.mouse.get_pos()
        if self.origin == "centre":
            x = self.x - self.w/2
            y = self.y - self.h/2
        else:
            x = self.x
            y = self.y

        if x <= pos[0] <= x + self.w and y <= pos[1] <= y + self.h:
            return True
        return False
def textObj(text, font, color = black):
    textsurface = font.render(text, True, color)
    return textsurface, textsurface.get_rect()


def hin():
   global lang
   lang = 0

def eng():
   global lang
   print("asdfasdfgsda666")
   lang = 1

def mar():
   global lang
   lang = 2

def bang():
   global lang
   lang = 3

def GUI():
    cnt=0
    global mapCurr, frame, closestLabel,lang
    loop = True

    confidence = 0

    tempt, hum, wind, status = weather()
    now = datetime.datetime.today().now()
    #getCity

    font20 = pygame.font.SysFont("Franklin Gothic Medium Cond", 20)
    font80 = pygame.font.SysFont("Franklin Gothic Heavy", 80)
    font50 = pygame.font.SysFont("Franklin Gothic Heavy", 50)
    font60 = pygame.font.SysFont("Franklin Gothic Heavy", 60)
    font24 = pygame.font.SysFont("Franklin Gothic Medium Cond", 24)
    font16 = pygame.font.SysFont("Franklin Gothic Medium Cond", 16)
    font36 = pygame.font.SysFont("Franklin Gothic Heavy", 36)
    font32 = pygame.font.SysFont("Franklin Gothic Heavy", 32)


    threading.Timer(1, getCity).start()
    label = "Human"

    getMap()
    threading.Timer(1, getMap).start()

    back = pygame.image.load("back.png")
    top = pygame.image.load("top.png")

    temp = pygame.image.load("temperature.png")
    winds = pygame.image.load("windspeed.png")
    humid = pygame.image.load("humid.png")
    #speak_thr.start()

    hindi = Button(1000, 50, 180, 50, hin)
    english = Button(1000, 110, 180, 50, eng)
    marathi = Button(1000, 170, 180, 50, mar)
    bangali = Button(1000, 230, 180, 50, bang)

    hindi.addText("Hindi", (0, 0), (200, 200, 200), 20)
    english.addText("English", (0, 0), (200, 200, 200), 20)
    marathi.addText("Marathi", (0, 0), (200, 200, 200), 20)
    bangali.addText("Bengali", (0, 0), (200, 200, 200), 20)

    advt = pygame.image.load('icons/advt.png')

    while loop:
        cnt=0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
                elif event.key == pygame.K_h:
                    print("adsfsdf")
                    lang = 0
                elif event.key == pygame.K_e:
                    lang = 1
                elif event.key == pygame.K_m:
                    lang = 2
                elif event.key == pygame.K_b:
                    lang = 3



        #_, frame = videoFeed.read()
        stime = time.time()
        label = "--"
        confidence = 0.0
        boxes = 0
        a = run(frame)

        closestLabel = None
        closestDist = float('inf')

        if 1:
           for color, result in zip(colors, results):
               tl = (result['topleft']['x'], result['topleft']['y'])
               br = (result['bottomright']['x'], result['bottomright']['y'])
               label = result['label']
               #print("tl is ",tl)
               vech=['car','motercycle','truck','bus']
               confidence = result['confidence']
               rec=['traffic light','car','motercycle','truck','bus','stop sign', 'turn left', 'turn right', 'go straight', '']
               #confidence*100>35 and (label in rec)
               if(a!=None):
                 if(a[0]!=None):
                   realHeight = 75
                   dist = (5.5*(realHeight)*360)/((a[3])*4.5)
                   if dist < closestDist:
                        closestDist = dist
                        closestLabel = str(a[0])
                   txt2 = '{}: {:.0f}% : Dist: {:.01f}cm'.format(a[0], confidence * 100, dist/10)
                   frame = cv2.putText(
                    frame, txt2, tuple(a[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 100, 200), 2)

               if(confidence*100>0 and (label in rec)):
                   text = '{}: {:.0f}%'.format(label, confidence * 100)
                   frame = cv2.rectangle(frame, tl, br, color, 5)
                   frame = cv2.putText(
                       frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                   if label in vech:
                       cnt+=1

                   realHeight = 75
                   if label == "person":
                    realHeight = 500
                   dist = (5.5*(realHeight)*360)/((br[1] - tl[1])*4.5)
                   if dist < closestDist:
                        closestDist = dist
                        closestLabel = str(label)

                   text = '{}: {:.0f}% : Dist: {:.0f}cm'.format(label, confidence * 100, dist/10)
                   frame = cv2.putText(
                    frame, text, tl, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 100, 200), 1)




        image = cv2.resize(frame, (vWidth, vHeight), interpolation=cv2.INTER_LINEAR)

        #speak_thr.join()

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.rot90(image)
        image = np.flip(image, 0)
        image = pygame.surfarray.make_surface(image)

        display.fill((0, 0, 0))

        #Live Feed
        drawBackground(20, 20, 900, 350)
        display.blit(image, (30, 30))

        # Confidence
        #confidence = (confidence + 1)%100

        display.blit(back, (515, 60))

        if not closestLabel or (closestLabel == "person"):
          confidence = 0


        points = [(0, 0), (0, 80), (6, 80), (6, 0)]
        coords = []
        angle = 60 + 240*(confidence)
        for point in points:
            coords.append(translate(600, 145, rotate(point, radians(angle), (3, 0))))


        pygame.draw.line(display, (91, 154, 213), (602.3164801755993, 149.43101789615605), (669.5063982331376, 187.59807621135332), 2)
        pygame.draw.line(display, (91, 154, 213), (529.217967697245, 187.40192378864668), (602.3164801755993, 149.43101789615605), 2)

        pygame.draw.polygon(display, (242, 119, 36), coords)
        display.blit(top, (555, 98))

        text = font36.render(str(int(confidence*100)), True, (255, 255, 255))
        display.blit(text, (575, 125))
        text = font20.render("%", True, (255, 255, 255))
        display.blit(text, (620, 135))

        # Prediction
        text = font24.render(str(closestLabel), True, (255, 255, 255))
        display.blit(text, (730, 90))

        text = font24.render(str("Do This Action"), True, (255, 255, 255))
        display.blit(text, (730, 140))

        if closestLabel in vehicles:
          dist = closestDist
        else:
          dist = 0

        text = font24.render("Distance From Next Vehicle: " + str("{:.01f}".format(dist/10)) + " cm", True, (255, 255, 255))
        display.blit(text, (600, 280))

        # Map
        drawBackground(20, 390, 440, 270)
        display.blit(mapCurr, (25, 395))


        # Weather
        drawBackground(480, 390, 440, 270)
        # Temp
        display.blit(temp, (513, 410))

        text = font36.render(str(int(tempt)), True, (146, 208, 80))
        display.blit(text, (533, 510))
        text = font16.render("C", True, (146, 208, 80))
        display.blit(text, (580, 515))

        # Wind
        display.blit(winds, (656, 410))
        text = font36.render(str(int(wind)), True, (255, 192, 0))
        display.blit(text, (686, 510))
        text = font16.render("m/s", True, (255, 192, 0))
        display.blit(text, (715, 515))

        # Humid
        display.blit(humid, (800, 410))
        text = font36.render(str(int(hum)), True, (255, 205, 255))
        display.blit(text, (830, 510))
        text = font16.render("%", True, (255, 205, 255))
        display.blit(text, (880, 510))

        text = font50.render(str(status.title()), True, (157, 190, 230))
        pos = text.get_rect()
        pos.center = (480 + 220, 390 + 220)
        display.blit(text, pos)

        hindi.draw()
        english.draw()
        marathi.draw()
        bangali.draw()

        display.blit(advt, (970, 350))

       # print(lang)

        pygame.display.update()
        if closestLabel:
          if(closestLabel in vehicles and closestDist < 17*10):
            if(lang==0):
              playsound("./sounds/vehicle_ahead_hi.mp3")
            elif(lang==1):
              playsound("./sounds/vehicle_ahead_en.mp3")
            elif(lang==2):
              playsound("./sounds/vehicle_ahead_mh.mp3")
            elif(lang==3):
              playsound("./sounds/vehicle_ahead_bn.mp3")
          else:
            if(closestLabel=="stop sign"):
              if(lang==0):
                playsound("./sounds/stop_hi.mp3")
              elif(lang==1):
                playsound("./sounds/stop_en.mp3")
              elif(lang==2):
                playsound("./sounds/stop_mh.mp3")
              elif(lang==3):
                playsound("./sounds/stop_bn.mp3")
            elif(closestLabel=="turn left"):
              if(lang==0):
                playsound("./sounds/tl_hi.mp3")
              elif(lang==1):
                playsound("./sounds/tl_en.mp3")
              elif(lang==2):
                playsound("./sounds/tl_mh.mp3")
              elif(lang==3):
                playsound("./sounds/tl_bn.mp3")
            elif(closestLabel=="turn right"):
              if(lang==0):
                playsound("./sounds/tr_hi.mp3")
              elif(lang==1):
                playsound("./sounds/tr_en.mp3")
              elif(lang==2):
                playsound("./sounds/tr_mh.mp3")
              elif(lang==3):
                playsound("./sounds/tr_bn.mp3")

        clock.tick(60)

GUI()
