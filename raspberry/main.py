from sense_hat import SenseHat
from random import randint
import time
import subprocess
import sys
from threading import Thread
import requests
import os

sense = SenseHat()
sense.set_rotation(270)

# Number of screens
MAX_SCREENS = 3

# Interval between broadcasts in seconds
BROADCAST_INTERVAL = 600

# Allowed RuuviTAGs and other sensors
SENSORS = { # Format: 'Tag name': 'location description'
    'SenseHAT': {
        'id': 1,
        'name': 'Sisätila'
    },
    'CC:72:6B:45:B7:A2': {
        'id': 2,
        'name': 'Parveke'
    }
}

def getRandomColor():
    return (randint(0,255), randint(0,255), randint(0,255))

def main():
    # Start broadcast thread
    thr = Thread(target=broadcast)
    thr.start()

    currentScreen = 1
    drawActive = True # toggle to turn drawing on or off
    while True:
        font_color = (255, 51, 255)
        background_color = (0, 50, 0)

        if(drawActive):
            if (currentScreen == 1): 
                showTemp(background_color, font_color)
            elif (currentScreen == 2):
                showHum(background_color, font_color)
            elif (currentScreen == 3):
                showPres(background_color, font_color)
            else:
                # Invalid screen
                pass

        for event in sense.stick.get_events():
            if (event.action == "pressed"):
                if (event.direction == "left" or event.direction == "right"):
                    currentScreen = getNextScreen(currentScreen, event.direction)
                elif (event.direction == "up"):
                    rotateScreen(90)
                elif (event.direction == "down"):
                    rotateScreen(-90)
                else:
                    # Joystick pressed
                    if (drawActive):
                        drawActive = False
                    else:
                        drawActive = True

        

def showTemp(bc, tc):
    #t = round(sense.get_temperature(), 1)
    t = round(sense.get_temperature_from_pressure(), 1)


    # Calibrate temp
    cpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
    cpu_temp = cpu_temp.decode("utf-8") # Convert bytes to str

    array = cpu_temp.split("=")
    array2 = array[1].split("'")

    cpu_tempc = float(array2[0])
    cpu_tempc = float("{0:.2f}".format(cpu_tempc))

    temp_calibrated = round(t - ((cpu_tempc - t)/2), 1)

    print('TT', t, 'TC', temp_calibrated, 'TH', round(sense.get_temperature_from_humidity(), 1), 'CC', cpu_tempc)

    message = "T: " + str(t) # sensor moved away from cpu, use actual temp
    sense.show_message(message, back_colour=bc, text_colour=tc, scroll_speed=0.1)

def showHum(bc, tc):
    h = round(sense.get_humidity(), 1)
    message = "H: " + str(h)
    sense.show_message(message, back_colour=bc, text_colour=tc, scroll_speed=0.1)

def showPres(bc, tc):
    p = int(sense.get_pressure())
    message = "P: " + str(p)
    sense.show_message(message, back_colour=bc, text_colour=tc, scroll_speed=0.1)

def getNextScreen(current, direction):
    if (direction == "left" and current == 1):
        current = MAX_SCREENS
    elif (direction == "left"):
        current = current - 1
    elif (direction == "right" and current == MAX_SCREENS):
        current = 1
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