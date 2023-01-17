# A LOT OF THESE ASSUMPTIONS MAY BE OUT OF DATE - REVIEW AT SOME POINT
# function assumes all data coming in as matrix of 'z' (depth) coordinates

#assumes data is coming in ordered, with all x, y, z coordinates w.r.t. 
#the start of the scanning sequence for x, y, and the scanner location in z
#(i.e., all linear transformations of data e.g. rotations, translations handled in
#other functions) - origin may change later

#considers x as direction along rail length, y as transverse direction, z as depth (downwards positive)
#LEFT-SIDE SENSOR TO SCAN L-R, USE LH COORDINATE SYSTEM; RIGHT-SIDE SENSOR SCANS R-L, RH COORD SYS
# ... maybe this doesn't make sense - could just scan L-R on both of them, not as if sense is very important

# ASSUMES SENSOR LOOKING DIRECTLY FROM TOP - if sensor mounted on an angle, need
# additional considerations (factoring sensor angle into any transformation matrices)

#code is to take in a matrix of depths along with the scanning differentials dx
#and dy (representing the change in real-world displacement from one row/col to 
#the next), and an optional rail profile (represented as a string, tied to a 
#function within the code), along with the sensor height then:
#   - provide a visual representation of the data i.e., pointcloud plot
#   - compute the (approx.) volume, max depth, max length, and max width of the
#     defect based on the given rail profile and data points
#   - "compute" the material that needs to be removed to get rid of the defect (put
#     this off for now - need to decide how much extra mat'l to remove; algorithm 
#     may change based on what tooling is used i.e., grinder vs ball endmill can't
#     match the same profile - not sure if this should even be handled. Note that also
#     want to get profile of mat'l for removal, not just volume (i.e., final milled/ground profile)
#   - parameters (plots, max depths, volume, etc) will be sent (or returned, depending
#     on how doing code integration) to another class to generate report

import numpy as np
import matplotlib.pyplot as mplot


def interpretData(scanData, dx, dy, sensorHeight, seq, railType="default", railScan=None, scanSide="left", folder='C:\\temp\\'):
    # check to make sure datatypes match expected - return error if not
    if not (type(scanData) is np.ndarray):
        # put error handling here - not sure what to do
        print("i don't know how this should be handled rn!")
    
    # being lazy and just casting numeric variables - if run into trouble later, do something better
    dx = float(dx)
    dy = float(dy)
    sensorHeight = float(sensorHeight)
    epsilon = 0.0001    # acceptable error w/ comparing scanned profile to rail profile

    numx, numy = scanData.shape

    # get defect-free rail profile w.r.t. sensor coordinate system
    # storing as 1D column vector for now (i.e., y coordinates only) - may change later
    railProfile = None
    if type(railScan is np.ndarray) and int(railScan.shape(0)) == numy:
        # treating data length mismatch as invalid - could maybe just interpolate values but eh
        railProfile = railScan
    else:
        railProfile = getProfile(railType, numy, dy, sensorHeight)
    # move to some initialization function maybe
    # arg for leaving here is that this way don't need numpy import in other classes


    # take scanData array, subtract off rail profile from each col, store into new matrix
    # in new array, set any values less than some small number to zero
    defectProfile = scanData - railProfile*np.ones(numy, numx) # dblchk that numx, numy in right order
    #for i in defectProfile:
    #    for j in i:
    #        if j <= epsilon:
    #            j = 0
    defectProfile[defectProfile <= epsilon] = 0 # if this doesn't work do other way
    
    maxDepth, defectLength, defectWidth, defectVolume = 0, 0, 0, 0
    if seq == 0:
        # only care about these params on 1st pass
        maxDepth = max(defectProfile)

        # probably non-optimal but fuck it
        defectLength    = getMaxContLength(defectProfile, dx)
        defectWidth     = getMaxContLength(np.transpose(defectProfile), dy) 
        #defectLength, defectWidth = getMaxDiscontLengths(defectProfile, dx, dy) # if going with discont lengths

        # get approx defect volume
        for i in range(numx-1):
            for j in range(numy-1):
                defectVolume += getElementVolume(dx, dy, defectProfile[j:j+1, i:i+1])

    workingProfile = None
    repairSuccess = False
    dfpType = wpType = ""

    if seq == 0:
        workingProfile = getRemovalProfile(defectProfile)
        generateToolpaths(defectProfile, workingProfile)    # would send this to machining module
        dfpType = "defect-initial"
        wpType = "machining-profile"
    elif seq == 1:
        workingProfile = getDepositionProfile(defectProfile)
        generateToolpaths(defectProfile, workingProfile)    # would send this to mat'l deposition
        dfpType = "post-machining"
        wpType = "deposition-profile"
    elif seq == 2:
        workingProfile = getGrindoutProfile(defectProfile)
        generateToolpaths(defectProfile, workingProfile)    # send to profile grinding module
        dfpType = "post-deposition"
        wpType = "grinding-profile"
    else:
        repairSuccess = profileMatch(defectProfile, railProfile)
        dfpType = "finished-profile"

    # need to check whether python stores as row or column vectors
    # probably a better way of doing this... this also might just straight up not work
    X = np.ones(numy, numx) * (range(0, numx) * dx)
    Y = np.transpose(np.ones(numx, numy) * (range(0, numy) * dy))
    
    # plot and save out defectProfile, workingProfile (unless seq == 3)
    dfPlot = mplot.figure()
    dfAx = dfPlot.add_subplot(projection='3d')
    dfAx.plot_wireframe(X, Y, defectProfile, rcount=numx, ccount=numy)
    dfPlot.savefig(folder + dfpType)
    mplot.close(dfPlot)
    plotFP = [folder + dfpType]

    if not workingProfile == None:
        wPlot = mplot.figure()
        wAx = wPlot.add_subplot(projection='3d')
        wAx.plot_wireframe(X, Y, workingProfile, rcount=numx, ccount=numy)
        wPlot.savefig(folder + wpType)
        mplot.close(wPlot)
        plotFP.append(folder + wpType)

    return maxDepth, defectLength, defectWidth, defectVolume, plotFP, repairSuccess # might not need all these returns

def generatePlot():
    print("do this later")
    # code to make 

def getRemovalProfile(profile):
    profile = profile * 1.12    # figuring extra 12% removal should be enough
    # at some point this needs to be curve-fit in a way thats machinable w/ selected tooling
    # either figuring this out later, or considering beyond scope of project
    return profile

def getDepositionProfile(profile):
    # would need to figure out how to determine required mat'l deposition profile
    return None

def getGrindoutProfile(profile):
    # would need to figure out how to determine final grindout profile
    return None

def generateToolpaths(initProf, finalProf, tool=""):
    # generate toolpaths to get profiles - beyond scope of project
    return None

def profileMatch(scanProf, railProf):
    # determine whether or not the repair was a success
    return True


# not sure if this is better or discontinuous is better - coding both, decide later
def getMaxContLength(matrix, ds):
    # not sure if it's better to do max continuous difference or max discontinuous difference
    # i.e., does length need to be in same row or can it be in different rows 
    maxElD = 0  # for storing difference between first and last column
    for i in matrix:
        nzInds = np.nonzero(i)
        elD = nzInds(max) - nzInds(min)
        if elD > maxElD:
            maxElD = elD        
    return maxElD * ds  # can only return length, width one at a time

def getMaxDiscontLengths(matrix, dx, dy):
    # not sure if it's better to do max continuous difference or max discontinuous difference
    # i.e., does length need to be in same row or can it be in different rows
    yinds, xinds = np.nonzero(matrix)   # check to make sure this is in the right order
    yElD = max(yinds) - min(yinds)
    xElD = max(xinds) - min(xinds)
    return xElD * dx, yElD * dy     # returning both length and width in one

def getElementVolume(dx, dy, delz):
    # NOTE: delz to be tuple, as (dz1, dz2, dz3, dz4)
    zAvg = sum(delz)/len(delz)
    return dx*dy*delz   # might think of something better later, going with this for now

def getProfile(railType, numy, dy, hSens):
    # THIS IS PROBABLY GOING TO GET MOVED TO ANOTHER FILE (some kind of calibration file)
    # if this happens, will just pass transformed defect-free rail profile
    # into main function, and get rid of railType and sensorHeight variables
    
    # THIS WHOLE FUNCTION IS GOING TO NEED SOME CONSIDERATION LATER - good chance i fucked something up
    # AT SOME POINT CHECK TO SEE IF LINSPACE INCLUDES LAST INDEX OR NOT - want to go from 0 to numy-1, inclusive
    railProfile = np.linspace(0, numy, dtype=np.ndarray) * dy
    
    
    # sensor position taken as origin for frame of reference;
    # assuming rail profiles defined based on the scanning profile (i.e., function defined for [0, dy*numy])
    # this might end up looking different depending on what functions end up looking like
    if railType == "standard1": # fill out with some standard rail profiles here
        print("hrm, splendid")
    elif railType == "standard2":
        print("ooga booga me big spaghetti code man")
    else:   # this also handles "default" case - not much use for var data in default case... change to none maybe
        # stretched inverted parabola, shifted over to match up center of data points, shifted up s.t. z(center)=0
        railProfile = -(1/32)*((railProfile - numy*dy/2.0) ** 2) # + (numy*dy/2.0)**2 -> want 0 at center

    return (hSens - railProfile) # assuming sensorHeight defined as dist from sensor to rail center


# CREATE TEST MATRIX FOR CODE - use some functionally-generated defect

if __name__ == "__main__" or __name__ == "InterpretData.Py":
    # PUT SOME TEST VALUES HERE AT SOME POINT
    scanData = 0
    dx = 0
    dy = 0
    sensorHeight = 0
    interpretData(scanData, dy, dy, sensorHeight)
