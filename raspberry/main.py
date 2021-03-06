from sense_hat import SenseHat
from random import randint
from queue import LifoQueue
from threading import Thread
import time
import subprocess
import sys
import multiprocessing as mp
import requests
import os
import logging

from sensor import Sensor
from moon import Moon
import ruuvi

# Interval between broadcasts in seconds
BROADCAST_INTERVAL = os.environ.get('WEATHERLOG_BC_INTERVAL')
try:
    BROADCAST_INTERVAL = int(BROADCAST_INTERVAL)
except ValueError:
    BROADCAST_INTERVAL = None
except TypeError:
    BROADCAST_INTERVAL = None

if (BROADCAST_INTERVAL is None):
    BROADCAST_INTERVAL = 300

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
    moonAnimation = None
    logger = None

    def __init__(self):
        self.sense = SenseHat()
        self.sense.set_rotation(0)

        self.initLogger()

        self.moonAnimation = Moon(3)
        

    def start(self):
        # Start broadcast thread
        thr = Thread(target=self.broadcast)
        thr.daemon = True
        thr.start()

        # Start ruuvi process watcher
        ruuvi_thr = Thread(target=self.ruuviProcessWatcher)
        ruuvi_thr.daemon = True
        ruuvi_thr.start()

        currentScreen = 0
        currentSensor = 0
        drawActive = True # toggle to turn drawing on or off

        moonActive = False

        # Initialize sensors with queue and process data
        for s in SENSORS:
            if (s.identifier != 'SenseHAT'):
                q, p = self.getRuuviQueue(s.identifier, 0)
                s.queue = q
                s.proc = p

        # Main loop
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
            else:
                # Show moon animation
                if (moonActive):
                    self.moonAnimation.play(self.sense)

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
                            if (moonActive):
                                moonActive = False
                            else:
                                moonActive = True

                            # Show information about current state of used sensor and screen
                            self.sense.show_message(SENSORS[currentSensor].name, back_colour=BACKGROUND_COLOR,
                                text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)
                            self.sense.show_message(SCREENS[currentScreen], back_colour=BACKGROUND_COLOR,
                                text_colour=FONT_COLOR, scroll_speed=SCROLL_SPEED)


    def showTemp(self, sensor):
        if (sensor.identifier == "SenseHAT"):
            t = round(self.sense.get_temperature_from_pressure(), 1)
        else:
            t = self.getNewestRuuvidata(sensor.queue)
            if (t == None):
                t = 'ND' # ND = NoData
            else:
                t = round(t.temperature, 1)

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
                h = round(h.humidity, 1)

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
                p = int(p.pressure)

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

    def initLogger(self):
        # create logger
        self.logger = logging.getLogger('weatherlog')
        self.logger.setLevel(logging.INFO)

        # Create console handler and set level to INFO
        ch = logging.FileHandler('weatherlog.log')
        ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)
        
        # add ch to logger
        self.logger.addHandler(ch)

    def getRuuviQueue(self, mac, searchTimeOut=5):
        #queue = LifoQueue()
        queue = mp.Queue()
        proc = mp.Process(target=ruuvi.Ruuvi.yieldToQueue, args=(mac, queue, searchTimeOut), daemon=False)
        proc.start()

        return queue, proc

    def getNewestRuuvidata(self, queue):
        allData = []
        while not queue.empty():
            allData.append(queue.get())

        if (len(allData) > 0):
            return allData[-1].data[1]
        return None

    def ruuviProcessWatcher(self):
        watchInterval = 3600
        while True:
            self.checkForRunningRuuviProcesses(0)
            time.sleep(watchInterval - (time.time() % watchInterval))

    # Check if ruuvi process is running and restart if needed
    def checkForRunningRuuviProcesses(self, searchTimeOut=0):
        for s in SENSORS:
            if (s.identifier != 'SenseHAT'):
                if (s.proc is not None):
                    if (not s.isRunning()):
                        s.proc.terminate()
                        
                        q, p = self.getRuuviQueue(s.identifier, searchTimeOut)
                        s.queue = q
                        s.proc = p

                        self.logger.warning('Created new Ruuvi process for sensor ' + str(s.identifier))


    def getRandomColor(self):
        return (randint(0,255), randint(0,255), randint(0,255))

    def broadcast(self):
        try:
            while True:
                time.sleep(BROADCAST_INTERVAL - (time.time() % BROADCAST_INTERVAL))
                print('Broadcast', time.time())
                self.logger.info('Broadcast started')

                url = os.environ.get('WEATHERLOG_URL')
                token = os.environ.get('WEATHERLOG_TOKEN')

                if (url and token):
                    for sensor in SENSORS:
                        if (sensor.identifier == 'SenseHAT'):
                            temp = round(self.sense.get_temperature_from_pressure(), 1)
                            hum = round(self.sense.get_humidity(), 1)
                            pres = int(self.sense.get_pressure())
                        else:
                            try:
                                rd = self.getNewestRuuvidata(sensor.queue)
                                temp = round(rd.temperature, 1)
                                hum = round(rd.humidity, 1)
                                pres = int(rd.pressure)
                            except AttributeError: # getNewestRuuvidata() result is None
                                self.logger.warning('Broadcast: getNewestRuuvidata() returned None for sensor"' + str(sensor.identifier) + '"')
                                continue

                        body = {
                            "temp": temp,
                            "humidity": hum,
                            "pressure": pres,
                            "accessToken": token,
                            "sensor_id": sensor.id
                        }
                        try:
                            res = requests.post(url, data=body, timeout=2.5)
                            print('RES', res)
                            self.logger.info('Broadcast for sensor "' + str(sensor.identifier) + '" successful')
                        except ConnectionRefusedError as e:
                            print('ERROR:', e)
                            self.logger.warning('Broadcast connection error: ' + str(e))
                        except Exception as e:
                            print('Unknown error:', e)
                            self.logger.warning('Unknown broadcast error: ' + str(e))

                else:
                    print('No url or token')
                    self.logger.info('Broadcast: No url or token')
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as err:
            self.logger.error('Error at broadcast. Error is: ' + str(err))

if __name__ == '__main__':
    wl = Weatherlog()
    wl.start()
