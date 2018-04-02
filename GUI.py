import pygame
import sys
from math import *

import cv2
import datetime
import numpy as np

import pyowm
import geocoder

import threading
import json
from urllib.request import urlopen
import time

from darkflow.net.build import TFNet

pygame.init()

options = {
    'model':'cfg/tiny-yolo.cfg',
    'load':'bin/tiny-yolo.weights',
    'threshold': 0.35,

}

videoFeed = cv2.VideoCapture(0)
vWidth = int(640*.75) # 480
vHeight = int(480*.75) # 360

width = 940
height = 650
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

city = "OFFLINE"

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
    try:
        g = geocoder('me')
        city = g.city
    except Exception:
        city = "OFFLINE"

    
def weather():
    lat, lan = getLatLan()
    if not lat:
        return 0, 0, 0, "- -"
    else:
        owm = pyowm.OWM('c84c2f255787c9dfc3d1c8b3795e4686')
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


def GUI():
    loop = True
    global frame, results, done, cap
    font20 = pygame.font.SysFont("Franklin Gothic Medium Cond", 20)
    font80 = pygame.font.SysFont("Franklin Gothic Heavy", 80)
    font50 = pygame.font.SysFont("Franklin Gothic Heavy", 50)
    font60 = pygame.font.SysFont("Franklin Gothic Heavy", 60)
    font24 = pygame.font.SysFont("Franklin Gothic Medium Cond", 24)
    font24 = pygame.font.SysFont("Franklin Gothic Medium Cond", 24)
    font36 = pygame.font.SysFont("Franklin Gothic Heavy", 36)
    font32 = pygame.font.SysFont("Franklin Gothic Heavy", 32)
    percent = 0

    temp, hum, wind, status = weather()
    now = datetime.datetime.today().now()
    #getCity()

    threading.Timer(1, getCity).start()

    currLat, currLan = 15, 20
    
    while loop:
        now = datetime.datetime.today().now()
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
        #_, image = videoFeed.read()
        stime = time.time()
        label = "--"
        confidence = 0.0
        boxes = 0
        if 1:
            for color, result in zip(colors, results):
                tl = (result['topleft']['x'], result['topleft']['y'])
                br = (result['bottomright']['x'], result['bottomright']['y'])
                label = result['label']
                #print(label)
                #vech=['car','motercycle','truck','bus']
                confidence = result['confidence']
                rec=['person','car','motercycle','truck','bus','stop sign']
                if(label in rec and (confidence*100>0)):
                    text = '{}: {:.0f}%'.format(label, confidence * 100)
                    frame = cv2.rectangle(frame, tl, br, color, 5)
                    frame = cv2.putText(
                        frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
                    boxes += 1
        image = cv2.resize(frame, (vWidth, vHeight), interpolation=cv2.INTER_LINEAR)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.rot90(image)
        image = np.flip(image, 0)
        image = pygame.surfarray.make_surface(image)
        
        display.fill((0, 0, 0))

        print(boxes)

        # Temperature
        drawBackground(60, 30, 160, 160)
        text = font20.render("Temperature", True, (255, 255, 255))
        display.blit(text, (70, 40))
        text = font80.render(str(int(temp)), True, (146, 208, 80))
        display.blit(text, (80, 70))
        text = font32.render("C", True, (146, 208, 80))
        display.blit(text, (180, 110))

        # Humidity
        drawBackground(280, 30, 160, 160)
        text = font20.render("Humidity", True, (255, 255, 255))
        display.blit(text, (290, 40))
        text = font80.render(str(int(hum)), True, (255, 205, 255))
        display.blit(text, (300, 70))
        text = font32.render("%", True, (255, 205, 255))
        display.blit(text, (400, 110))

        # Wind Speed
        drawBackground(500, 30, 160, 160)
        text = font20.render("Wind Speed", True, (255, 255, 255))
        display.blit(text, (510, 40))
        text = font80.render(str(int(wind)), True, (255, 192, 0))
        display.blit(text, (530, 70))
        text = font32.render("m/s", True, (255, 192, 0))
        display.blit(text, (580, 110))

        # Status
        drawBackground(720, 30, 160, 160)
        text = font20.render("Overall Status", True, (255, 255, 255))
        display.blit(text, (730, 40))
        text = font50.render(str(status.title()), True, (157, 190, 230))
        display.blit(text, (740, 90)) 
    
        # Live Video Feed
        drawBackground(30, 240, 500, 380)
        display.blit(image, (40, 250))

        # Confidence
        drawBackground(550, 240, 360, 190)
        pygame.draw.ellipse(display, (91, 154, 213), (560, 250, 170, 170))
        pygame.draw.ellipse(display, (40, 40, 40), (580, 270, 130, 130))

        #percent = (percent + 1)%100

        points = [(0, 0), (0, 80), (6, 80), (6, 0)]
        coords = []
        angle = 60 + 240*(confidence)
        for point in points:
            coords.append(translate(645, 335, rotate(point, radians(angle), (3, 0))))

        pygame.draw.line(display, (91, 154, 213), (647.3164801755993, 339.43101789615605), (576.4201938371021, 376.494700705745), 2)
        pygame.draw.line(display, (91, 154, 213), (718.2127665140965, 367.63266491343285), (647.3164801755993, 339.43101789615605), 2)

        pygame.draw.polygon(display, (242, 119, 36), coords)

        pygame.draw.ellipse(display, (60, 60, 60), (600, 290, 90, 90))

        text = font36.render(str(int(confidence*100)), True, (255, 255, 255))
        display.blit(text, (615, 310))
        text = font24.render("%", True, (255, 255, 255))
        display.blit(text, (660, 320))

        # Prediction
        text = font24.render(str(label), True, (255, 255, 255))
        display.blit(text, (740, 270))

        text = font24.render(str("Do This Action"), True, (255, 255, 255))
        display.blit(text, (750, 330))
        

        # Date Time Location
        drawBackground(550, 460, 360, 160)
        text = font24.render(str("Notification"), True, (166, 166, 166))
        display.blit(text, (570, 470))

        signLat, signLan = 50, 70
      
        currLan += .05

        distLast = ((signLat - currLat)**2 + (signLan - currLan)**2)**.5

        #if distLast < 10:
        text = "Next Symbol at {:.02f} units".format(distLast)

        text = font24.render(str(text), True, (255, 255, 255))
        display.blit(text, (570, 500))
        
        text = font24.render("Number Of Objects Detected: " + str(boxes), True, (255, 255, 255))
        display.blit(text, (570, 550))
        
        pygame.display.update()
        clock.tick(60)

GUI()
