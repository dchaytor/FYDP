# general assumptions moved to bottom of module
import numpy as np
import matplotlib.pyplot as mplot

def interpretData(scanData, dx, dy, sensorHeight, seq, railType="default", railScan=None, scanSide="left", folder='C:\\temp\\'):
    #scanData = sensorHeight - scanData # if actually scanning in data, need to do this to put w.r.t. scanner ref frame

    # should check to make sure datatypes match expected & return error if not but eh
    if not (type(scanData) is np.ndarray):
        # there should prob be some error handling here, but should be ok since we can control data passed in
        scanData = np.array(scanData)
    
    # being lazy and just casting numeric variables - if run into trouble later, do something better
    dx = float(dx)
    dy = float(dy)
    sensorHeight = float(sensorHeight)
    epsilon = 0.001    # acceptable error w/ comparing scanned profile to rail profile

    numy, numx = scanData.shape     # shape is gonna be as (cols, rows), so (y, x)

    # get defect-free rail profile w.r.t. sensor coordinate system
    # storing as 1D column vector for now (i.e., y coordinates only) - may change later
    railProfile = None
    if type(railScan) is np.ndarray:
        if int(railScan.shape(0)) == numy:
            # treating data length mismatch as invalid - could maybe just interpolate values but eh
            # this is bad actually bc of noise, uncertainty in orientation, etc. but it's never getting run so w/e
            railProfile = railScan  
    else:
        railProfile = getSliceProfile(railType, numy, dy, sensorHeight)
    
    # take scanData array, subtract off rail profile from each col, store into new matrix
    defectProfile = scanData - railProfile  # assumes non-curved rail profile; would need mtx transform otherwise
    
    # set any values less than some small number to zero
    defectProfile[defectProfile <= epsilon] = 0
    defectIdx = np.nonzero(defectProfile)   # indices where defect is
    dfBounds = ((defectIdx[0].min(), defectIdx[0].max() + 1), 
        defectIdx[1].min(), defectIdx[1].max() + 1)   # prob a better way but eh
    
    maxDepth, defectLength, defectWidth, defectVolume = 0, 0, 0, 0
    if seq == 0:
        # only care about these params on 1st pass
        maxDepth = defectProfile.max()

        # probably non-optimal but fuck it
        defectLength    = getMaxContLength(defectProfile, dx)
        defectWidth     = getMaxContLength(np.transpose(defectProfile), dy) 
        #defectLength, defectWidth = getMaxDiscontLengths(defectProfile, dx, dy) # if going with discont lengths

        # get approx defect volume
        for i in range(numx-1):
            for j in range(numy-1):
                # +2 is since end point is non-inclusive
                defectVolume += getElementVolume(dx, dy, defectProfile[j:j+2, i:i+2])

    workingProfile = np.array([])
    repairSuccess = False
    dfpType = wpType = ""

    if seq == 0:
        workingProfile = getRemovalProfile(scanData, defectProfile, dfBounds)
        generateToolpaths(scanData, workingProfile)    # would send this to machining module
        dfpType = "defect-initial"
        wpType = "machining-profile"
    elif seq == 1:
        workingProfile = getDepositionProfile(scanData, defectProfile, dfBounds)
        generateToolpaths(scanData, workingProfile)    # would send this to mat'l deposition
        dfpType = "post-machining"
        wpType = "deposition-profile"
    elif seq == 2:
        workingProfile = getGrindoutProfile(scanData, defectProfile, dfBounds)
        generateToolpaths(scanData, workingProfile)    # send to profile grinding module
        dfpType = "post-deposition"
        wpType = "grinding-profile"
    else:
        repairSuccess = profileMatch(defectProfile)
        dfpType = "finished-profile"

    # creating grid based on number of indices in x and y and distance per step
    X, Y = np.meshgrid(np.arange(0, numx) * dx, np.arange(0, numy) * dy)
    
    # plot and save out defectProfile, workingProfile (unless seq == 3)
    #dfPlot = mplot.figure()
    #dfAx = dfPlot.add_subplot(projection='3d')
    #dfAx.plot_wireframe(X, Y, defectProfile, rcount=numx, ccount=numy)
    #dfPlot.savefig(folder + dfpType)
    #mplot.close(dfPlot)
    #plotFP = [folder + dfpType]

    # DON'T want to be just plotting defectProfile since it's normalized to rail profile
    # should be plotting rail profile, coloured based on depths of defectprofile
    plotFP = [plot3D(X, Y, scanData, numx, numy, folder + dfpType)]


    if workingProfile.size != 0: # unga bunga moment
        #wPlot = mplot.figure()
        #wAx = wPlot.add_subplot(projection='3d')
        #wAx.plot_wireframe(X, Y, workingProfile, rcount=numx, ccount=numy)
        #wPlot.savefig(folder + wpType)
        #mplot.close(wPlot)
        #plotFP.append(folder + wpType)
        print(workingProfile.shape) # giving (0,) - need to figure out why

        plotFP.append([plot3D(X, Y, workingProfile, numx, numy, folder + wpType)])


    return maxDepth, defectLength, defectWidth, defectVolume, plotFP, repairSuccess # might not need all these returns


def getRemovalProfile(rProfile, dfProfile, dfBounds):
    (rm, rM), (cm, cM) = dfBounds

    # figuring extra 12% removal should be enough
    rmprofile = rProfile[rm:rM, cm:cM] - abs(dfProfile[rm:rM, cm:cM] * 1.12)
    return rmprofile


def getDepositionProfile(rProfile, dfProfile, dfBounds):
    # would need to figure out how to determine required mat'l deposition profile
    return None


def getGrindoutProfile(rProfile, dfProfile, dfBounds):
    # would need to figure out how to determine final grindout profile
    return None


def generateToolpaths(initProf, finalProf, tool=""):
    # generate toolpaths to get profiles - beyond scope of project
    return None


def profileMatch(defectProfile):
    # determine whether or not the repair was a success
    '''
    if defectProfile.sum() == 0:
        return True
    else:
        return False
    '''
    return True
    

# not sure if this is better or discontinuous is better - coding both, decide later
def getMaxContLength(matrix, ds):
    # not sure if it's better to do max continuous difference or max discontinuous difference
    # i.e., does length need to be in same row or can it be in different rows 
    maxElD = 0  # for storing difference between first and last column
    for i in matrix:
        nzInds = (np.nonzero(i))[0]

        if not nzInds.shape == (0,):
            elD = nzInds.max() - nzInds.min()
            if elD > maxElD:
                maxElD = elD

    return maxElD * ds  # can only return length, width one at a time


def getMaxDiscontLengths(matrix, dx, dy):
    # not sure if it's better to do max continuous difference or max discontinuous difference
    # i.e., does length need to be in same row or can it be in different rows
    yinds, xinds = np.nonzero(matrix)   # check to make sure this is in the right order
    yElD = yinds.max() - yinds.min()
    xElD = xinds.max() - xinds.min()
    return xElD * dx, yElD * dy     # returning both length and width in one


def getElementVolume(dx, dy, delz):
    # NOTE: delz to be 2x2 array, as [(dz1, dz2), dz3, dz4)]
    zAvg = delz.sum()/4.0   # always going to be 4 elements; just hard coding in
    return dx*dy*zAvg   # might think of something better later, going with this for now


def getSliceProfile(railType, numy, dy, hSens):
    # get 1D y profile
    railProfile = np.arange(0, numy, dtype=np.ndarray) * dy
        
    # sensor position taken as origin for frame of reference;
    # assuming rail profiles defined based on the scanning profile (i.e., function defined for [0, dy*numy])
    if railType == "standard1": # fill out with some standard rail profiles here
        print("hrm, splendid")
    elif railType == "standard2":
        print("ooga booga me big spaghetti code man")
    else:   # this also handles "default" case - not much use for var data in default case... change to none maybe
        # stretched inverted parabola, shifted over to match up center of data points, shifted up s.t. z(center)=0
        railProfile = -(1/64)*((railProfile - (numy-1)*dy/2.0) ** 2) # + (numy*dy/2.0)**2 -> want 0 at center
    
    return np.array((railProfile - hSens)[:, None]) # assuming sensorHeight defined as dist from sensor to rail center

def plot3D(X, Y, Z, rcount, ccount, fp=None):
    # code to generate generic 3d wireframe plot (maybe add another parameter & generalize for other 3D plots)
    plt = mplot.figure()
    ax = plt.add_subplot(projection='3d')
    ax.plot_wireframe(X, Y, Z, rcount=rcount, ccount=ccount)    # might use something other than wireframe, idk
    ax.set_box_aspect((np.ptp(X), np.ptp(Y), np.ptp(Z)))    # normalizing axes
    
    '''
    ideas for plot (if possible):
    - hide x/y/z gridlines, put a scale line in instead
    - colour based on defect profile (i.e., further deviation from standard profile gives colour gradient)
        -> look into different mplot functions, surf commands, idk
    - make sure to save out interactive plot if possible (so can resize/pan etc)
    DO THIS STUFF AFTER REST OF INTERPRETDATA, SYSTEMREPORTS ARE VERIFIED
    -> prob just leave these for now, and do them after MDR
    '''

    if not fp == None and False:
        # get rid of "and False" when actually testing system
        plt.savefig(fp)
        mplot.close(plt)
    else:
        mplot.show()

    return fp

if __name__ == "__main__" or __name__ == "InterpretData.Py":
    # at some point split up __name__ == so have options for testing from module/actually running

    # reminder for sanity: shape is given as (y, x) since (rows, cols)
    dx = .5
    dy = .5
    numx, numy = 100, 20
    sensorHeight = 0.5
    sliceData = getSliceProfile(None, numy, dy, sensorHeight)
    
    # code to visualize profile slice; looks good, so commenting out
    '''
    print(type(sliceData))
    print(sliceData.shape)
    mplot.figure()
    mplot.plot(sliceData)
    mplot.xlim(0, 20)
    mplot.ylim(-10, 10)
    mplot.show()
    '''
    X, Y = np.meshgrid(np.arange(0, numx) * dx, np.arange(0, numy) * dy)
    scanData = (np.multiply(np.ones((numy, numx)), sliceData))
    
    #print(scanData - sliceData) # this works as expected
    
    #print(np.around(scanData, 1))  # checking to see that matrix was generated properly
    #print(X.shape, Y.shape, sliceData.shape, scanData.shape)

    #plot3D(X, Y, scanData, numy, numx) 

    
    test = np.array(((0, 0, 0, 0), (0, 2, 0, 0), (0,3,0,0), (0, 0, 0, 0)))
    print(test)
    testIdx = np.nonzero(test)
    testBounds = ((testIdx[0].min(), testIdx[0].max() + 1), (testIdx[1].min(), testIdx[1].max() + 1))
    (a, b), (c, d) = testBounds
    
    #print(test[testBounds[0], testBounds[1]])
    #print(test[(1,2) * (1, 2)])
    #print(test[testBounds[0][0]:testBounds[0][1], testBounds[1][0]:testBounds[1][1]])
    #print(test[a:b, c:d])
    


    '''
    ret = interpretData(scanData, dx, dy, sensorHeight, seq=0)

    print(f"Max Depth: {ret[0]}")
    print(f"Defect Length: {ret[1]}")
    print(f"Defect Width: {ret[2]}")
    print(f"Defect Volume: {ret[3]}")
    '''
    






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
