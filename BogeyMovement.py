import pygame                   # for controller
import RPi.GPIO as GPIO         # for raspberry pi
from gpiozero import Servo      # for servo control
from gpiozero import Motor      # for DC motor control
from gpiozero import Button     # for buttons
import time


# Controller Buttons - DS4 setup
bogieDrive = 1                  # Bogie drive forward/backward - Left Stick
setBrake = 2                    # Bogie brakes activated - Square
resetBrake = 0                  # Bogie brakes deactivated - X
scanForward = 11                # Bogie scanner move forward - D-pad Up
scanBackward = 12               # Bogie scanner move backward - D-pad Down
scanStop = 13                   # Bogie scanner stop - D-pad Left
eStopOneButtonOne = 4           # Bogie shutdown - Left Trigger
eStopOneButtonTwo = 5           # Bogie shutdown - Right Trigger
eStopTwoButtonOne = 7           # Bogie shutdown - Left Stick
eStopTwoButtonTwo = 8           # Bogie shutdown - Right Stick

# Control Params
leftStickForwardMin = -0.95     # Min axis value on left stick to move forward
leftStickBackwardMin = 0.95     # Min axis value on left stick to move backward
leftTriggerMin = 0.5            # Min axis value to e-stop
rightTriggerMin = 0.5           # Min axis value to e-stop
driveMotorSpeed = 0.5
scanMotorSpeed = 0.5
maxServoAngle = 1               # Set servo to max angle: ((max/270)*2 - 1)
minServoAngle = -1              # Set servo to min angle: ((min/270)*2 - 1)

# Set pins
driveForwardPin = 23        # GPIO pin set to drive bogie forward
driveBackwardPin = 24       # GPIO pin set to drive bogie backward
# driveEnablePin =          # GPIO pin set to enable motor controller
scanBackwardPin = 4         # GPIO pin set to move scanner backward
scanForwardPin = 17         # GPIO pin set to move scanner forward
scanEnablePin = 27          # GPIO pin set to enable motor controller
# forwardButtonStopPin =    # GPIO pin set to stop scanner once scan ends and return
# rearButtonStopPin =       # GPIO pin set to stop scanner once returned
brakeServoPin = 18          # GPIO pin set for brakes


def initializeControl():
    global driveMotor, scanMotor, servoMotor

    # Initialize
    pygame.init()       # initialize pygame
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    print(joysticks)

    # Raspberry Pi setup
    GPIO.cleanup() # clear GPIOs
    GPIO.setmode(GPIO.BCM) # setup GPIO call mode for raspberry pi

    driveMotor = Motor(driveForwardPin, driveBackwardPin)
    scanMotor = Motor(scanForwardPin, scanBackwardPin, scanEnablePin)
    servoMotor = Servo(brakeServoPin)
    # frontButton = Button(forwardButtonStopPin)
    # rearButton = Button(rearButtonStopPin)
    # Encoder not set up - not using

def forwardDrive(driveSpeed):
    driveMotor.forward(driveSpeed)
    print("Moving Forward")

def backwardDrive(driveSpeed):
    driveMotor.backward(driveSpeed)
    print("Moving Backward")

def stopDrive():
    driveMotor.stop()

def activateBrakes():
    if servoMotor.value != maxServoAngle:    
        servoMotor.value = maxServoAngle     
        print("Activating Brake")

def deactivateBrakes():
    if servoMotor.value != minServoAngle:
        servoMotor.value = minServoAngle
        print("Deactivating Brake")

def forwardScan(scanSpeed):
    scanMotor.forward(scanSpeed)

def backwardScan(scanSpeed):
    scanMotor.backward(scanSpeed)

def stopScan():
    scanMotor.stop()

# def moveScannerBack():
#     # Start moving scanner backward
#     scan = True
#     scanMotor.backward()

#     # Stop motor and stop scanner movement once scanner hits button
#     while scan:
#         rearButton.wait_for_press()
#         scanMotor.stop()
#         scan = False
        
#     return scan

# def moveScannerForward():
#     # Start moving scanner forward
#     scan = True
#     scanMotor.forward()

#     # Stop motor and end scan once scanner hits button
#     while scan:
#         frontButton.wait_for_press()
#         scanMotor.stop()
#         scan = False
    
#     return scan

# def scanSequence():
#     # Start scan loop
#     scanning = True
#     # Block driving
#     pygame.event.set_blocked(pygame.JOYAXISMOTION)
#     print("Starting Scan")
#     while scanning:
#         # Start scanning
#         scanning = moveScannerForward()

#         # trigger scanner data read-in, line-by-line, based on encoder data
#         # need to have set dy to know what encoder values to take data readings at
#         # store scanner data in some sort of 2D mapping (numpy array or list of tuples possibly)
#         # don't worry about dx, dy, as this is handled later - just leave based on indices
#         scanData = None
        
#     # End scan loop
#     print("End Scan")

#     # Wait two seconds
#     time.sleep(2)
    
#     # Start return loop
#     print("Returning to Start Position")
#     returning = True

#     while returning:
#         # Return scanner to start position
#         returning = moveScannerBack()

#     # End return loop
#     print("Returned to Start")
    
#     # Allow driving
#     pygame.event.set_allowed(pygame.JOYAXISMOTION)

#     return scanData

def shutDown():
    pygame.quit()
    GPIO.cleanup()



