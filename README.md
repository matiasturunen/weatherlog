# Weatherlog
Weather data logging utility for apartment environment monitoring. Includes Raspberry Pi app to monitor and save information to remote server. Server on the other hand is responsible for keeping hold of data and to create graphs from it.

## Features
 - Support for multiple sensors
 - Will feature RuuviTAG support (as soon as I get one in my hands...)
 - Show current weather information on SenseHAT LED matrix
 - LED matrix controlled with SenseHATs joystick

## Work In Progress
This software is under development. In theory it does work, but in practice the RPi app will stop responding after some time. I'm working on that. Also the RPi-Server connection does not yet support multiple sensors

## How to use

1. Install Raspberry Pi code to the Pi with temp, hum and pres sensors (I'm planning to use SENSE HAT)
2. Install remote server software
3. Generate access token for the Pi and save it to the Pi. Connect Pi to the internet.
4. Cross your fingers and wait for first databurst =)

