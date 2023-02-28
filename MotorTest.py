import RPi.GPIO as GPIO         # for raspberry pi
from gpiozero import Servo      # for servo control
from gpiozero import Motor      # for DC motor control
from gpiozero import Button     # for buttons
import time


# Set pins
driveForwardPin = 23        # GPIO pin set to drive bogie forward
driveBackwardPin = 24       # GPIO pin set to drive bogie backward
driveEnablePin = 18         # GPIO pin set to enable motor controller
scanForwardPin = 17         # GPIO pin set to move scanner forward
scanBackwardPin = 4         # GPIO pin set to move scanner backward
scanEnablePin = 27          # GPIO pin set to enable motor controller
brakeServoPin = 16          # GPIO pin set for brakes

 # Raspberry Pi setup
GPIO.cleanup() # clear GPIOs
GPIO.setmode(GPIO.BCM) # setup GPIO call mode for raspberry pi

driveMotor = Motor(driveForwardPin, driveBackwardPin, driveEnablePin)
scanMotor = Motor(scanForwardPin, scanBackwardPin, scanEnablePin)
servoMotor = Servo(brakeServoPin)


def forwardDrive(driveSpeed):
    driveMotor.forward(driveSpeed)
    time.sleep(2)
    driveMotor.stop()
    time.sleep(2)

def backwardDrive(driveSpeed):
    driveMotor.backward(driveSpeed)
    time.sleep(2)
    driveMotor.stop()
    time.sleep(2)

def activateBrakes(maxServoAngle):
    if servoMotor.value != maxServoAngle:    
        servoMotor.value = maxServoAngle     
        print("Activating Brake")

def deactivateBrakes(minServoAngle):
    if servoMotor.value != minServoAngle:
        servoMotor.value = minServoAngle
        print("Deactivating Brake")

def moveScannerBack():
    scanMotor.backward(1)
    time.sleep(2)
    scanMotor.stop()
    time.sleep(2)

def moveScannerForward():
    scanMotor.forward(1)
    time.sleep(2)
    scanMotor.stop()
    time.sleep(2)



