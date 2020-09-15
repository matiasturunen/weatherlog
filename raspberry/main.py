from sense_hat import SenseHat
from time import sleep
from random import randint
import subprocess
import sys

sense = SenseHat()
MAX_SCREENS = 3

def getRandomColor():
    return (randint(0,255), randint(0,255), randint(0,255))

def main():
    currentScreen = 1
    while True:
        sense.clear()

        font_color = (255, 51, 255)
        background_color = (0, 50, 0)

        if (currentScreen == 1): 
            showTemp(background_color, font_color)
        elif (currentScreen == 2):
            showHum(background_color, font_color)
        elif (currentScreen == 3):
            showPres(background_color, font_color)
        else:
            pass

        for event in sense.stick.get_events():
            if (event.action == "pressed"):
                if (event.direction == "left" or event.direction == "right"):
                    currentScreen = getNextScreen(currentScreen, event.direction)
                elif (event.direction == "up"):
                    pass
                elif (event.direction == "down"):
                    pass
                else:
                    # Joystick pressed
                    sense.clear()
                    sys.exit(0)



        
def showTemp(bc, tc):
    t = round(sense.get_temperature(), 1)


    # Calibrate temp
    cpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
    cpu_temp = cpu_temp.decode("utf-8") # Convert bytes to str

    array = cpu_temp.split("=")
    array2 = array[1].split("'")

    cpu_tempc = float(array2[0])
    cpu_tempc = float("{0:.2f}".format(cpu_tempc))

    temp_calibrated = round(t - ((cpu_tempc - t)/5.466), 1)

    print('TT', t, 'TC', temp_calibrated)

    message = "T: " + str(temp_calibrated)
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


if __name__ == '__main__':
    main()