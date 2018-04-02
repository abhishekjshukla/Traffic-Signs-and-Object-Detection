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

pygame.init()

videoFeed = cv2.VideoCapture(0)
vWidth = int(640*.75)
vHeight = int(480*.75)

width = 940
height = 650
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

city = "OFFLINE"

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
        url = "http://ipinfo.io/json"
        response = urlopen(url)
        data = json.load(response)

        city = data['city']
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
    
    while loop:
        now = datetime.datetime.today().now()
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
        _, image = videoFeed.read()
        image = cv2.resize(image, (vWidth, vHeight), interpolation=cv2.INTER_LINEAR)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.rot90(image)
        image = pygame.surfarray.make_surface(image)
        
        display.fill((0, 0, 0))

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

        percent = (percent + 1)%100

        points = [(0, 0), (0, 80), (6, 80), (6, 0)]
        coords = []
        angle = 60 + 240*(percent/100.0)
        for point in points:
            coords.append(translate(645, 335, rotate(point, radians(angle), (3, 0))))

        pygame.draw.line(display, (91, 154, 213), (647.3164801755993, 339.43101789615605), (576.4201938371021, 376.494700705745), 2)
        pygame.draw.line(display, (91, 154, 213), (718.2127665140965, 367.63266491343285), (647.3164801755993, 339.43101789615605), 2)

        pygame.draw.polygon(display, (242, 119, 36), coords)

        pygame.draw.ellipse(display, (60, 60, 60), (600, 290, 90, 90))

        text = font36.render(str(int(percent)), True, (255, 255, 255))
        display.blit(text, (615, 310))
        text = font24.render("%", True, (255, 255, 255))
        display.blit(text, (660, 320))

        # Prediction
        text = font24.render(str("Predicted Symbol"), True, (255, 255, 255))
        display.blit(text, (740, 270))

        text = font24.render(str("Do This Action"), True, (255, 255, 255))
        display.blit(text, (750, 330))
        

        # Date Time Location
        drawBackground(550, 460, 360, 160)
        text = font24.render(str("Location: "), True, (166, 166, 166))
        display.blit(text, (570, 470))

        threading.Timer(1, getCity).start()
        #city = "Kolkata"
        text = font24.render(str(city), True, (255, 255, 255))
        display.blit(text, (660, 470))

        date, day = getWeekDate(now)
        text = font24.render(str(day), True, (255, 255, 255))
        display.blit(text, (800, 470))

        text = font60.render(str("{:02}".format(now.hour)), True, (166, 166, 166))
        display.blit(text, (560, 500))
        text = font24.render(str("Hrs"), True, (166, 166, 166))
        display.blit(text, (630, 530))

        text = font60.render(str("{:02}".format(now.minute)), True, (166, 166, 166))
        display.blit(text, (670, 500))
        text = font24.render(str("Mins"), True, (166, 166, 166))
        display.blit(text, (740, 530))

        text = font60.render(str("{:02}".format(now.second)), True, (166, 166, 166))
        display.blit(text, (785, 500))
        text = font24.render(str("Secs"), True, (166, 166, 166))
        display.blit(text, (860, 530))


        text = font32.render(str(date), True, (166, 166, 166))
        pos = text.get_rect()
        pos.center = (550 + 180, 590)
        display.blit(text, pos)

        pygame.display.update()
        clock.tick(60)

GUI()
