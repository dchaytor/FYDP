#function assumes all data coming in as matrix of 'z' (depth) coordinates

#assumes data is coming in ordered, with all x, y, z coordinates w.r.t. 
#the start of the scanning sequence for x, y, and the scanner location in z
#(i.e., all linear transformations of data e.g. rotations, translations handled in
#other functions) - origin may change later

#treats x as direction along rail length, y as transverse direction, z as depth (downwards positive)
#LEFT-SIDE SENSOR TO SCAN L-R, USE LH COORDINATE SYSTEM; RIGHT-SIDE SENSOR SCANS R-L, RH COORD SYS
# ... maybe this doesn't make sense - could just scan L-R on both of them, not as if sense is very important

# ASSUMES SENSOR LOOKING DIRECTLY FROM TOP - if sensor mounted on an angle, need
# additional considerations (factoring sensor angle into any transformation matrices)

#code is to take in a matrix of depths along with the scanning differentials dx
#and dy (representing the change in real-world displacement from one row/col to 
#the next), and an optional rail profile (represented as a string, tied to a 
#function within the code), along with the sensor height then:
#   - provide a visual representation of the data i.e., pointcloud plot (may also
#     connect adjacent points to form mesh)
#   - compute the (approx.) volume, max depth, max length, and max width of the
#     defect based on the given rail profile and data points
#   - "compute" the material that needs to be removed to get rid of the defect (put
#     this off for now - need to decide how much extra mat'l to remove; algorithm 
#     may change based on what tooling is used i.e., grinder vs ball endmill can't
#     match the same profile - not sure if this should even be handled. Note that also
#     want to get profile of mat'l for removal, not just volume (i.e., final milled/ground profile)
#   - parameters (plots, max depths, volume, etc) will be sent (or returned, depending
#     on how doing code integration) to another function to generate report (report not
#     generated here)

import numpy as np
import matplotlib as mplot


def interpretData(scanData, dx, dy, sensorHeight, railType="default", railScan=None, scanSide="left"):
    # check to make sure datatypes match expected - return error if not
    if not (type(scanData) is np.ndarray):
        # put error handling here - not sure what to do
        print("i don't know how this should be handled rn!")
    
    # being lazy and just casting numeric variables - if run into trouble later, do something better
    dx = float(dx)
    dy = float(dy)
    sensorHeight = float(sensorHeight)

    # getting length of rows/columns in matrix; might need error checking
    # (could get a valueerror if shape tuple is wrong size)
    numx, numy = scanData.shape

    # get defect-free rail profile w.r.t. sensor coordinate system
    # storing as 1D column vector for now (i.e., y coordinates only) - may change later
    # if so, just use np.multiply to multiply vector with ones array
    railProfile = None
    if type(railScan is np.ndarray) and int(railScan.shape(0)) == numy:
        # treating data length mismatch as invalid - could maybe just interpolate values but eh
        railProfile = railScan
    else:
        railProfile = getProfile(railType, numy, dy, sensorHeight)
    # ^ this is probably going to get moved to another file + final value just passed into this one

    # JUST WRITING PSEUDOCODE FOR REST OF FUNCTION FOR NOW:
    # take scanData array, subtract off rail profile from each col, store into new matrix
    # in new array, set any values less than some small number to zero
    
    # run a max() on the new matrix - index of this will give max depth in scanData matrix
    # get length, width by looking at furthest left, right, up, and down elements that are non-zero
    #   ->> use numpy.nonzero to find non-zero indices, then figure out from there
    #   ->> convert to lengths by taking the differences between indices and multiplying by dy or dx

    # loop through new matrix elementwise, excluding last row and last col
    # at each point, look at (i, j) through (i+1, j+1):
    #   -> send differential depth values to getElementVolume, add to running volume sum
    

    # STILL NEED TO FIGURE OUT MATERIAL REMOVAL, VISUAL DATA REPRESENTATION (3D PLOTS, ETC)




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