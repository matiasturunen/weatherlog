from sense_hat import SenseHat
from random import randint
import time
import subprocess
import sys
from threading import Thread
from queue import LifoQueue
import multiprocessing as mp
import requests
import os

from sensor import Sensor
import ruuvi

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

class Weatherlog:

    prevRuuviData = None
    sense = None

    def __init__(self):
        self.sense = SenseHat()
        self.sense.set_rotation(0)
        

    def start(self):
        # Start broadcast thread
        thr = Thread(target=self.broadcast)
        thr.daemon = True
        thr.start()

        currentScreen = 0
        currentSensor = 0
        drawActive = True # toggle to turn drawing on or off

        for s in SENSORS:
            if (s.identifier != 'SenseHAT'):
                s.queue = self.getRuuviQueue(s.identifier, 0)

        
        while True:
            if(drawActive):
                if (currentScreen == 0): 
                    self.showTemp(SENSORS[currentSensor])
                elif (currentScreen == 1):
                    self.showHum(SENSORS[currentSensor])
                elif (currentScreen == 2):
                    self.showPres(SENSORS[currentSensor])
                else:
                    # Invalid screen
                    pass

            for event in self.sense.stick.get_events():
                if (event.action == "pressed"):
                    if (event.direction == "left" or event.direction == "right"):
                        currentScreen = self.getNextScreen(currentScreen, event.direction)

                        self.sense.show_message(SCREENS[currentScreen], back_colour=BACKGROUND_COLOR, 
                            text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

                    elif (event.direction == "up" or event.direction == "down"):
                        currentSensor = self.switchSensor(currentSensor, event.direction)

                        self.sense.show_message(SENSORS[currentSensor].name, back_colour=BACKGROUND_COLOR, 
                            text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

                    else:
                        # Joystick pressed
                        if (drawActive):
                            drawActive = False
                            self.sense.clear()
                        else:
                            drawActive = True

    def showTemp(self, sensor):
        if (sensor.identifier == "SenseHAT"):
            t = round(self.sense.get_temperature_from_pressure(), 1)
        else:
            t = self.getNewestRuuvidata(sensor.queue)
            if (t == None):
                t = 'ND' # ND = NoData
            else:
                t = t.temperature

        message = "T: " + str(t)
        print(message)
        self.sense.show_message(message, back_colour=BACKGROUND_COLOR, text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

    def showHum(self, sensor):
        if (sensor.identifier == "SenseHAT"):
            h = round(self.sense.get_humidity(), 1)
        else:
            h = self.getNewestRuuvidata(sensor.queue)
            if (h == None):
                h = 'ND' # ND = NoData
            else:
                h = h.humidity

        message = "H: " + str(h)
        print(message)
        self.sense.show_message(message, back_colour=BACKGROUND_COLOR, text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

    def showPres(self, sensor):
        if (sensor.identifier == "SenseHAT"):
            p = int(self.sense.get_pressure())
        else:
            p = self.getNewestRuuvidata(sensor.queue)
            if (p == None):
                p = 'ND' # ND = NoData
            else:
                p = p.pressure

        message = "P: " + str(p)
        print(message)
        self.sense.show_message(message, back_colour=BACKGROUND_COLOR, text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)

    def getNextScreen(self, current, direction):
        if (direction == "left" and current == 0):
            current = len(SCREENS)-1
        elif (direction == "left"):
            current = current - 1
        elif (direction == "right" and current == len(SCREENS)-1):
            current = 0
        else:
            current = current + 1

        return current

    def switchSensor(self, current, direction):
        if (direction == "up" and SENSORS[current] == SENSORS[0]):
            current = len(SENSORS) - 1
        elif (direction == "up"):
            current = current - 1
        elif (direction == "down" and SENSORS[current] == SENSORS[len(SENSORS) - 1]):
            current = 0
        else:
            current = current + 1

        return current

    def rotateScreen(self, degrees):
        if (self.sense.rotation + degrees >= 360):
            self.sense.set_rotation((self.sense.rotation + degrees) - 360)
        elif (sense.rotation + degrees < 0): # degrees can be negative
            self.sense.set_rotation((self.sense.rotation + 360) + degrees)
        else:
            self.sense.set_rotation(self.sense.rotation + degrees)

    # def getSingleRuuviData(self, mac, searchTimeOut=5):
    #     startTime = time.time()

    #     ######################################
    #     #
    #     # KORJAA: Useita prosesseja kertyy eivätkä sammu vaikka pitäisi
    #     #
    #     ######################################

    #     queue = mp.Queue()
    #     qval = None

    #     p = mp.Process(target=ruuvi.Ruuvi.getSingle, args=(mac, queue, searchTimeOut))
    #     p.start()
    #     p.join(searchTimeOut)

    #     if (not queue.empty()):
    #         qval = queue.get()
            
    #     while True:
    #     #     if (not queue.empty()):
    #     #         p.join()
    #     #         qval = queue.get()
    #     #         break

    #         if (time.time() - startTime > searchTimeOut):
    #             print('Terminate started')
    #             p.terminate()
    #             print('Process terminated')
    #             break

    #     try:
    #         p.terminate()
    #         p.close()
    #     except ValueError as e:
    #         print('Error at process close:', e)
    #     return qval

    def getRuuviQueue(self, mac, searchTimeOut=5):
        #queue = LifoQueue()
        queue = mp.Queue()
        proc = mp.Process(target=ruuvi.Ruuvi.yieldToQueue, args=(mac, queue, searchTimeOut), daemon=False)
        proc.start()

        return queue

    def getNewestRuuvidata(self, queue):
        print('FCALL')
        if (not queue.empty()):
            data = queue.get()
            print('Data from queue:', data.timestamp, data.data)
            if (self.prevRuuviData is None):
                self.prevRuuviData = data
                return data.data[1]
            else:
                if (data.timestamp > self.prevRuuviData.timestamp):
                    self.prevRuuviData = data
                    return data.data[1]
        return None


        # now = time.time()
        # while True:
        #     if (queue.empty()):
        #         break
        #     else:
        #         data = queue.get()



    def getRandomColor(self):
        return (randint(0,255), randint(0,255), randint(0,255))

    def broadcast(self):
        while True:
            time.sleep(BROADCAST_INTERVAL - (time.time() % BROADCAST_INTERVAL))
            print('Broadcast', time.time())

            temp = round(self.sense.get_temperature_from_pressure(), 1)
            hum = round(self.sense.get_humidity(), 1)
            pres = int(self.sense.get_pressure())

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
    wl = Weatherlog()
    wl.start()
