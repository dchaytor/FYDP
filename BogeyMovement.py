import pygame                   # for controller
import RPi.GPIO as GPIO         # for raspberry pi
from gpiozero import Servo      # for servo control
from gpiozero import Motor      # for DC motor control
import time


# Controller Buttons - DS4 setup
bogieDrive = 1                  # Bogie drive forward/backward - Left Stick
setBrake = 2                    # Bogie brakes activated - Square
resetBrake = 0                  # Bogie brakes deactivated - X
scanForward = 11                # Bogie scanner move forward - D-pad Up
eStopOneButtonOne = 4           # Bogie shutdown - Left Trigger
eStopOneButtonTwo = 5           # Bogie shutdown - Right Trigger
eStopTwoButtonOne = 7           # Bogie shutdown - Left Stick
eStopTwoButtonTwo = 8           # Bogie shutdown - Right Stick

# Control Params
leftStickForwardMin = -0.95     # Min axis value on left stick to move forward
leftStickBackwardMin = 0.95     # Min axis value on left stick to move backward
leftTriggerMin = 0.5            # Min axis value to e-stop
rightTriggerMin = 0.5           # Min axis value to e-stop
motorSpeed = 0.5                
maxServoAngle = 1               # Set servo to max angle: ((max/270)*2 - 1)
minServoAngle = -1              # Set servo to min angle: ((min/270)*2 - 1)

# Set pins
driveForwardPin = 1         # GPIO pin set to drive bogie forward - change pin# when decided
driveBackwardPin = 2        # GPIO pin set to drive bogie backward - change pin# when decided
scanForwardPin = 3          # GPIO pin set to move scanner forward - change pin# when decided
scanBackwardPin = 4         # GPIO pin set to move scanner backward - change pin# when decided
scanForwardStopPin = 5      # GPIO pin set to stop scanner once scan ends and return - change pin# when decided
scanBackwardStopPin = 6     # GPIO pin set to stop scanner once returned - change pin# when decided
brakeServoPin = Servo(7)    # GPIO pin set for brakes - change pin# when decided
driveMotor = Motor(forward = driveForwardPin, backward = driveBackwardPin)
scanMotor = Motor(forward = scanForwardPin, backward = scanBackwardPin)


def initializeControl():
    # Initialize
    pygame.init()       # initialize pygame
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    print(joysticks)

    # Raspberry Pi setup
    GPIO.setmode(GPIO.BOARD) # setup GPIO call mode for raspberry pi
    GPIO.cleanup() # clear GPIOs

    # Set pin type
    GPIO.setup(scanForwardStopPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)         # Set pin as input defaulted to low
    GPIO.setup(scanBackwardStopPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)        # Set pin as input defaulted to low

def forwardDrive(driveSpeed):
    driveMotor.forward(driveSpeed)
    print("Moving Forward")

def backwardDrive(driveSpeed):
    driveMotor.backward(driveSpeed)
    print("Moving Backward")

def stopDrive():
    driveMotor.stop()

def activateBrakes():
    if brakeServoPin.value != maxServoAngle:    
        brakeServoPin.value = maxServoAngle     
        print("Activating Brake")

def deactivateBrakes():
    if brakeServoPin.value != minServoAngle:
        brakeServoPin.value = minServoAngle
        print("Deactivating Brake")

def moveScannerBack():
    # Start moving scanner backward
    scanMotor.backward()
    # Stop motor and stop scanner movement once scanner hits button
    scan = True
    while scan:
        if GPIO.input(scanBackwardStopPin) == GPIO.HIGH:
            scanMotor.stop()
            scan = False
        return scan

def moveScannerForward():
    # Start moving scanner forward
    scanMotor.forward()
    # Stop motor and end scan once scanner hits button
    scan = True
    while scan:
        if GPIO.input(scanForwardStopPin) == GPIO.HIGH:
            scanMotor.stop()
            scan = False
        return scan

def scanSequence():
    # Start scan loop
    scanning = True
    # Block driving
    pygame.event.set_blocked(pygame.JOYAXISMOTION)
    print("Start Scan")
    while scanning:
        # Start scanning
        scanning = moveScannerForward()

        # trigger scanner data read-in, line-by-line, based on encoder data
        # need to have set dy to know what encoder values to take data readings at
        # store scanner data in some sort of 2D mapping (numpy array or list of tuples possibly)
        # don't worry about dx, dy, as this is handled later - just leave based on indices
        scanData = None
        
    # End scan loop
    print("End Scan")

    # Wait two seconds
    time.sleep(2)
    
    # Start return loop
    print("Return to Starting Position")
    returning = True

    while returning:
        # Return scanner to start position
        returning = moveScannerBack()

    # End return loop
    print("Returned to Start")
    
    # Allow driving
    pygame.event.set_allowed(pygame.JOYAXISMOTION)

    return scanData

def shutDown():
    pygame.quit()
    GPIO.cleanup()



