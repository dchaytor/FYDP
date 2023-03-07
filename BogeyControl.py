import InterpretData            # make sure this is the right way to do this
import BogeyMovement as BM      # class holding actual actions
import SystemReports
import time
import pygame

def initialize():
    initPass = True
    
    BM.initializeControl()
    BM.activateBrakes()

    # full system would use scanner to determine rail profile, scanner height
        # height would just be min returned value (possibly averaged over scan dist)
        # profile just full scan-in in rail frame of ref, then pick closest std profile
            # or, if none match, take profile as average of scan path then pass that to other functions
            # can use same var, then judge what was done later by checking type (str or float array)
    scannerHeight = 60  # setting as 60mm for now
    railProfile = "default"
    dx, dy = 1, 1       # setting both to 1mm for now; in reality, would have to figure out based on sensor

    # test to make sure movements work - may leave this out of project
        # could put this in, but pointless without imu etc to verify mvmt works

    # move scanners until next side reached, move back
    # BM.scanSequence() # not using - do not call

    # if any tests fail, set initPass = False, gen. err report 

    # would also check cameras, scanner, data storage to make sure systems work

    return [scannerHeight, railProfile, initPass, dx, dy] 

def manualCtrl(h, profile, dx, dy):
    shutdown = False
    timeOut = 3600  # times out after 3600s (1h)
    startTime = time.asctime(time.localtime())
    refTime = time.time()
    nRep, nFail = 0, 0
    reportParams = []

    while(not shutdown):
        if time.time() - refTime > timeOut:
            shutdown = True
        
        # loop thru, checking for button inputs (when figured out)
        # when a button input is recognized, run appropriate movement command
        # make sure to put in an emergency stop button too
        # whenever a button input is recognized, set refTime = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shutdown = True
            if event.type == pygame.JOYBUTTONDOWN:
                # SQUARE
                if pygame.joystick.Joystick(0).get_button(BM.setBrake):
                    BM.activateBrakes()
                # CIRCLE
                elif pygame.joystick.Joystick(0).get_button(BM.resetBrake):
                    BM.deactivateBrakes()
                # TRIANGLE
                elif pygame.joystick.Joystick(0).get_button(BM.scanForward):
                    BM.forwardScan(BM.scanMotorSpeed)
                # X
                elif pygame.joystick.Joystick(0).get_button(BM.scanBackward):
                    BM.backwardScan(BM.scanMotorSpeed)
                # CLICK TOUCH PAD
                elif pygame.joystick.Joystick(0).get_button(BM.scanStop):
                    BM.stopScan()
                # R2
                elif pygame.joystick.Joystick(0).get_button(BM.bogieForward):
                    BM.forwardDrive()
                # L2
                elif pygame.joystick.Joystick(0).get_button(BM.bogieBackward):
                    BM.backwardDrive()
                # L1
                elif pygame.joystick.Joystick(0).get_button(BM.bogieStop):
                    BM.stopDrive()
                # PRESS LEFT STICK AND RIGHT STICK
                elif pygame.joystick.Joystick(0).get_button(BM.eStopButtonOne) and pygame.joystick.Joystick(0).get_button(BM.eStopButtonTwo):
                    shutdown = True
                refTime = time.time()
                print(refTime)
                print(event)
            # if event.type == pygame.JOYAXISMOTION:
            #     # LEFT STICK BACKWARD
            #     if pygame.joystick.Joystick(0).get_axis(BM.bogieDrive) > BM.leftStickBackwardMin:
            #         pygame.event.set_blocked(pygame.JOYBUTTONDOWN)
            #         BM.backwardDrive(BM.driveMotorSpeed)
            #     # LEFT STICK FORWARD
            #     elif pygame.joystick.Joystick(0).get_axis(BM.bogieDrive) < BM.leftStickForwardMin:
            #         pygame.event.set_blocked(pygame.JOYBUTTONDOWN)
            #         BM.forwardDrive(BM.driveMotorSpeed)
            #     # LEFT STICK CENTER
            #     elif pygame.joystick.Joystick(0).get_axis(BM.bogieDrive) < BM.leftStickBackwardMin and pygame.joystick.Joystick(0).get_axis(BM.bogieDrive) > BM.leftStickForwardMin:
            #         BM.stopDrive()
            #     # PRESS L2 and R2
            #     elif pygame.joystick.Joystick(0).get_axis(BM.eStopOneButtonOne) > BM.leftTriggerMin and pygame.joystick.Joystick(0).get_axis(BM.eStopOneButtonTwo) > BM.rightTriggerMin:
            #         shutdown = True

        # on-event scan sequence
        # probably just return everything from InterpretData then send to reports as required
        # remember to pass in sequence var: 0 = 1st scan, 1 = post-machining scan, 2 = post-deposition scan
        # would save out plots in InterpretData, but send to reports here (using just filepath as str)
        params = []
        for seq in range(0, 3): # make sure this sends out the correct number of times
            scanData = BM.scanSequence()   # need to write this still lol
            params.append(InterpretData.interpretData(scanData, dx, dy, h, seq))
        
        fp = SystemReports.repairReport(params)
        rPass = (params[-1])[-1] # make sure this accesses the last element of the last tuple of the list
        reportParams.append(params[0][0:4], rPass, fp) # double check this
        
        if rPass:    
            nRep += 1
        else:
            nFail += 1
        
        # make it so that all reports return the name they're saved under


    endTime = time.asctime(time.localtime())

    # generate shutdown report
    # need to create tuple to send to defectReport
    dfFile = SystemReports.defectReport(reportParams)
    SystemReports.shutdownReport(nRep, nFail, startTime, endTime, dfFile)

    # figure out how to shut down system safely
    BM.shutDown()


def bogeyDisplay(state, message=""):
    # ideally want a segmented (or other simple) display on bogey
    print("figure this out later, or maybe not at all")
    # state will allow to choose from a set of predefined messages; optional message param
    # is for if wanting to print one-off or custom messages not captured by states

if __name__ == "__main__" or __name__ == "BogeyControl.py":
    # send to initialize function, then send to main loop
    [h, profile, initPass, dx, dy] = initialize()

    if initPass:
        print("Initialized")
        manualCtrl(h, profile, dx, dy)
    else:
        # would print message to bogey display console (once figured out)
        print("ERROR")