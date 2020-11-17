from sense_hat import SenseHat
from random import randint
import time
import subprocess
import sys
from threading import Thread
import requests
import os

from sensor import Sensor
import ruuvi

sense = SenseHat()
sense.set_rotation(270)

# Interval between broadcasts in seconds
BROADCAST_INTERVAL = 30

# Allowed RuuviTAGs and other sensors
SENSORS = (
    Sensor(1, 'SISATILA', 'SenseHAT'),
    Sensor(2, 'PARVEKE', 'CC:72:6B:45:B7:A2')
)

SCREENS = (
    "LAMPO",
    "KOSTEUS",
    "PAINE"
)

BACKGROUND_COLOR = (0, 50, 0)
FONT_COLOR = (255, 51, 255)

SCROLL_SPEED = 0.1

def main():
    # Start broadcast thread
    thr = Thread(target=broadcast)
    thr.daemon = True
    thr.start()

    currentScreen = 0
    currentSensor = 0
    drawActive = True # toggle to turn drawing on or off
    
    while True:
        if(drawActive):
            if (currentScreen == 0): 
                showTemp(SENSORS[currentSensor])
            elif (currentScreen == 1):
                showHum(SENSORS[currentSensor])
            elif (currentScreen == 2):
                showPres(SENSORS[currentSensor])
            else:
                # Invalid screen
                pass

        for event in sense.stick.get_events():
            if (event.action == "pressed"):
                if (event.direction == "left" or event.direction == "right"):
                    currentScreen = getNextScreen(currentScreen, event.direction)

                    sense.show_message(SCREENS[currentScreen], back_colour=BACKGROUND_COLOR, 
                        text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

                elif (event.direction == "up" or event.direction == "down"):
                    currentSensor = switchSensor(currentSensor, event.direction)

                    sense.show_message(SENSORS[currentSensor].name, back_colour=BACKGROUND_COLOR, 
                        text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

                else:
                    # Joystick pressed
                    if (drawActive):
                        drawActive = False
                        sense.clear()
                    else:
                        drawActive = True

def showTemp(sensor):
    if (sensor.identifier == "SenseHAT"):
        t = round(sense.get_temperature_from_pressure(), 1)
    else:
        t = getSingleRuuviData(sensor.identifier).temperature

    message = "T: " + str(t)
    print(message)
    sense.show_message(message, back_colour=BACKGROUND_COLOR, text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

def showHum(sensor):
    if (sensor.identifier == "SenseHAT"):
        h = round(sense.get_humidity(), 1)
    else:
        h = getSingleRuuviData(sensor.identifier).humidity

    message = "H: " + str(h)
    print(message)
    sense.show_message(message, back_colour=BACKGROUND_COLOR, text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

def showPres(sensor):
    if (sensor.identifier == "SenseHAT"):
        p = int(sense.get_pressure())
    else:
        p = getSingleRuuviData(sensor.identifier).pressure

    message = "P: " + str(p)
    print(message)
    sense.show_message(message, back_colour=BACKGROUND_COLOR, text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

def getNextScreen(current, direction):
    if (direction == "left" and current == 0):
        current = len(SCREENS)-1
    elif (direction == "left"):
        current = current - 1
    elif (direction == "right" and current == len(SCREENS)-1):
        current = 0
    else:
        current = current + 1

    return current

def switchSensor(current, direction):
    if (direction == "up" and SENSORS[current] == SENSORS[0]):
        current = len(SENSORS) - 1
    elif (direction == "up"):
        current = current - 1
    elif (direction == "down" and SENSORS[current] == SENSORS[len(SENSORS) - 1]):
        current = 0
    else:
        current = current + 1

    return current

def rotateScreen(degrees):
    if (sense.rotation + degrees >= 360):
        sense.set_rotation((sense.rotation + degrees) - 360)
    elif (sense.rotation + degrees < 0): # degrees can be negative
        sense.set_rotation((sense.rotation + 360) + degrees)
    else:
        sense.set_rotation(sense.rotation + degrees)

def getSingleRuuviData(mac, searchTimeOut=5):
    ruuviList = []
    for x in ruuvi.Ruuvi.getRuuviData(mac, searchTimeOut):
        ruuviList.append(x[1])
        break
    if len(ruuviList) > 0:
        return ruuviList[0]
    else:
        return None

def getRandomColor():
    return (randint(0,255), randint(0,255), randint(0,255))

def broadcast():
    while True:
        time.sleep(BROADCAST_INTERVAL - (time.time() % BROADCAST_INTERVAL))
        print('Broadcast', time.time())

        temp = round(sense.get_temperature_from_pressure(), 1)
        hum = round(sense.get_humidity(), 1)
        pres = int(sense.get_pressure())

        url = os.environ.get('WEATHERLOG_URL')
        token = os.environ.get('WEATHERLOG_TOKEN')
        body = {
            "temp": temp,
            "humidity": hum,
            "pressure": pres,
            "accessToken": token
        }
        if (url and token):
            try:
                res = requests.post(url, data=body, timeout=2.5)
                print('RES', res)
            except ConnectionRefusedError as e:
                print('ERROR:', e)
            except Exception as e:
                print('Unknown error:', e)

        else:
            print('No url or token')

if __name__ == '__main__':
    main()