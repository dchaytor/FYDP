import RPi.GPIO as GPIO         # for raspberry pi
from gpiozero import Servo      # for servo control
from gpiozero import Motor      # for DC motor control
from gpiozero import Button     # for buttons
import time


# Set pins
driveForwardPin = 23        # GPIO pin set to drive bogie forward
driveBackwardPin = 24       # GPIO pin set to drive bogie backward
driveEnablePin = 18         # GPIO pin set to enable motor controller
scanBackwardPin = 4         # GPIO pin set to move scanner backward
scanForwardPin = 17         # GPIO pin set to move scanner forward
scanEnablePin = 27          # GPIO pin set to enable motor controller
brakeServoPin = 18          # GPIO pin set for brakes

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
    brake = True
    while brake:
        servoMotor.min()
        time.sleep(1)
        servoMotor.mid()
        time.sleep(1)
        servoMotor.max()
        time.sleep(1)
        brake = False

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

def testScanner():
    moveScannerBack(0.5)
    moveScannerForward(0.5)

def testDrive():
    forwardDrive(0.1)
    backwardDrive(0.1)

def testServo():
    activateBrakes(1)
    deactivateBrakes(1)

    



