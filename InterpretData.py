# local repo at C:/Users/dunca/OneDrive/Documents/4B/FYDP/FYDP
# general assumptions moved to bottom of module
import numpy as np
import matplotlib.pyplot as mplot
from matplotlib import cm as colmap
from matplotlib.colors import CenteredNorm

def interpretData(scanData, dx, dy, sensorHeight, seq, railType="default", railScan=None, scanSide="left", folder='C:/Users/dunca/OneDrive/Documents/4B/FYDP/FYDP'):
    #scanData = sensorHeight - scanData # if actually scanning in data, need to do this to put w.r.t. scanner ref frame
    
    # should check to make sure datatypes match expected & return error if not but eh
    if not (type(scanData) is np.ndarray):
        # there should prob be some error handling here, but should be ok since we can control data passed in
        scanData = np.array(scanData)
        
    #scanData = scanData.astype(float) # prob don't need this
    # being lazy and just casting numeric variables - if run into trouble later, do something better
    dx = float(dx)
    dy = float(dy)
    sensorHeight = float(sensorHeight)
    epsilon = 1e-4    # acceptable error w/ comparing scanned profile to rail profile

    numy, numx = scanData.shape     # shape is gonna be as (cols, rows), so (y, x)
    
    # get defect-free rail profile w.r.t. sensor coordinate system
    # storing as 1D column vector for now (i.e., y coordinates only) - may change later
    idealRailProfile = None
    if type(railScan) is np.ndarray:
        if int(railScan.shape(0)) == numy:
            # treating data length mismatch as invalid - could maybe just interpolate values but eh
            # this is bad actually bc of noise, uncertainty in orientation, etc. but it's never getting run so w/e
            idealRailProfile = railScan  
    else:
        idealRailProfile = getSliceProfile(railType, numy, dy, sensorHeight)
       
    
    # take scanData array, subtract off rail profile from each col, store into new matrix
    # represents defects as positive values for now
    defectProfile = idealRailProfile - scanData # assumes non-curved rail profile; would need mtx transform otherwise
    defectProfile[abs(defectProfile) <= epsilon] = 0    # set any values less than some small number to zero
    defectIdx = np.nonzero(defectProfile)   # indices where defect is
    
    
    dfBounds = ()
    
    if np.any(defectIdx):   # making sure there's a defect before running below eqn
        dfBounds = ((defectIdx[0].min(), defectIdx[0].max() + 1), 
            (defectIdx[1].min(), defectIdx[1].max() + 1))   # prob a better way but eh
        
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
    plotFP = ""
    
    # creating grid based on number of indices in x and y and distance per step
    X, Y = np.meshgrid(np.arange(0, numx) * dx, np.arange(0, numy) * dy)
    
    # generating working profiles, determining norm for colourplot
    if dfBounds:        # should return true if defect is non-empty
        if seq == 0:
            workingProfile, defectCloseup, wpX, wpY = getRemovalProfile(scanData, defectProfile, dfBounds, X, Y)
            generateToolpaths(scanData, workingProfile)    # would send this to machining module
            dfpType = "defect-initial"
            wpType = "machining-profile"
        elif seq == 1:
            workingProfile, defectCloseup, wpX, wpY = getDepositionProfile(scanData, idealRailProfile, dfBounds, X, Y)
            generateToolpaths(scanData, workingProfile)    # would send this to mat'l deposition
            dfpType = "post-machining"
            wpType = "deposition-profile"
        elif seq == 2:
            workingProfile, defectCloseup, wpX, wpY = getGrindoutProfile(scanData, idealRailProfile, dfBounds, X, Y)
            generateToolpaths(scanData, workingProfile)    # send to profile grinding module
            dfpType = "post-deposition"
            wpType = "grinding-profile"

        #norm = mplot.Normalize(defectProfile.min(), defectProfile.max())
        norm = CenteredNorm(halfrange = max(abs(defectProfile.min()), abs(defectProfile.max())))
   
    else:   # if defect is empty, profile matches rest of rail
        repairSuccess = profileMatch(defectProfile)
        dfpType = "finished-profile"
        norm = CenteredNorm(halfrange=epsilon)  # showing that all w/in tolerance by end
  

    # plotting rail:
    cmap = colmap.viridis  # decent looking ones: winter, twilight, viridis
    colours = cmap(norm(defectProfile))
    plotFP = [plot3D_colourgrad(X, Y, scanData, colours, norm, cmap, numx, numy, folder + dfpType)]

    # DON'T want to be just plotting defectProfile since it's normalized to rail profile
    # should be plotting rail profile, coloured based on depths of defectprofile
    #plotFP = [plot3D(X, Y, scanData, numx, numy, folder + dfpType)] 
    
    # plotting closeup of defect, working profile
    if workingProfile.size != 0: # unga bunga moment
        numdfy, numdfx = workingProfile.shape
        plotFP.append([plot3D(wpX, wpY, defectCloseup, numdfx, numdfy, folder + wpType + '_initial')])
        plotFP.append([plot3D(wpX, wpY, workingProfile, numdfx, numdfy, folder + wpType + '_final')])


    return workingProfile, dfBounds    # returning different params for testing
    #return maxDepth, defectLength, defectWidth, defectVolume, plotFP, repairSuccess # might not need all these returns but eh


def getRemovalProfile(rProfile, dfProfile, dfBounds, X, Y):
    (rm, rM), (cm, cM) = dfBounds
    rmX, rmY = X[rm:rM, cm:cM], Y[rm:rM, cm:cM]
    dprofile = rProfile[rm:rM, cm:cM]
    # figuring extra 12% removal should be enough
    rmprofile = dprofile - abs(dfProfile[rm:rM, cm:cM] * 1.12)
    return rmprofile, dprofile, rmX, rmY


def getDepositionProfile(rProfile, target_profile, dfBounds, X, Y):
    # need to figure out how to determine required mat'l deposition profile:
    # -> something similar to but slightly larger than final rail profile
    # -> want bounds to extend slightly past dfBounds in all directions (s.t. making sure df covered up)
    (rm, rM), (cm, cM) = dfBounds

    eidx = 3    # extra indices +- dfBounds to weld onto
    rm -= eidx
    rM += eidx
    cm -= eidx
    cM += eidx

    dfprofile = rProfile[rm:rM, cm:cM]  # saving out a bit more than needed but eh who cares

    dpX, dpY = X[rm:rM, cm:cM], Y[rm:rM, cm:cM]

    extraTol = .2    # 2mm extra profile from top everywhere (somewhat arbitrary, lacking more well informed solution)

    dpProfile = (np.multiply(np.ones((rM - rm, cM - cm)), target_profile[rm:rM])) + extraTol    # for ideal + 2mm
    #dpProfile = np.ones((rM - rm, cM - cm)) * target_profile[rm:rM].max() + extraTol    # for same value everywhere

    return dpProfile, dfprofile, dpX, dpY


def getGrindoutProfile(rProfile, target_profile, dfBounds, X, Y):
    # final grindout profile is just going to be defect-free rail profile...
    (rm, rM), (cm, cM) = dfBounds
    dfprofile = rProfile[rm:rM, cm:cM]

    goX, goY = X[rm:rM, cm:cM], Y[rm:rM, cm:cM]
    goprofile = (np.multiply(np.ones((rM - rm, cM - cm)), target_profile[rm:rM]))  # make sure shape matches goX, goY
    return goprofile, dfprofile, goX, goY


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
    
    return np.array((railProfile - hSens)[:, None]).astype(float) # assuming sensorHeight defined as dist from sensor to rail center

def plot3D(X, Y, Z, rcount, ccount, fp=""):
    # code to generate generic 3d wireframe plot (maybe add another parameter & generalize for other 3D plots)
    plt = mplot.figure()
    ax = plt.add_subplot(projection='3d')
    ax.plot_wireframe(X, Y, Z, rcount=rcount, ccount=ccount)    # might use something other than wireframe, idk
    ax.set_box_aspect((np.ptp(X), np.ptp(Y), np.ptp(Z)))    # normalizing axes

    # make sure to go back at some point and switch code to use savefig instead
    # also, try to get image to crop when using savefig
    if not fp == "" and False:
        # get rid of "and False" when actually testing system
        plt.savefig(fp)
        mplot.close(plt)
    else:
        mplot.show()

    return fp

def plot3D_colourgrad(X, Y, Z, colours, norm, cmap, rcount, ccount, fp=''):
    
    plt = mplot.figure()
    ax = plt.add_subplot(projection='3d')
    surf = ax.plot_surface(X, Y, Z, rcount=rcount, ccount=ccount, facecolors=colours, shade=False)
    surf.set_facecolor((0, 0, 0, 0))
    ax.set_box_aspect((np.ptp(X), np.ptp(Y), np.ptp(Z)))    # normalizing axes
    plt.colorbar(colmap.ScalarMappable(norm=norm, cmap=cmap), shrink=0.5, aspect=10)

    # hiding gridlines, axes ticks
    #mplot.axis('off')  # nevermind, this looks like shit

    # adding scale bar # can't find a way to do this that wouldn't be a massive PITA
    #scalebar = AnchoredSizeBar(ax.transData, 0.1, '1mm', 'lower center')
    #ax.add_artist(scalebar)

    # make sure to go back at some point and switch code to use savefig instead
    # also, try to get image to crop when using savefig
    mplot.show()

    return fp



if __name__ == "__main__" or __name__ == "InterpretData.Py":
    # at some point split up __name__ == so have options for testing from module/actually running

    # reminder for sanity: shape is given as (y, x) since (rows, cols)
    dx = .5
    dy = .5
    numx, numy = 50, 20
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
    perfectRail = (np.multiply(np.ones((numy, numx)), sliceData))
    
    #print(scanData - sliceData) # this works as expected
    
    #print(np.around(scanData, 1))  # checking to see that matrix was generated properly
    #print(X.shape, Y.shape, sliceData.shape, scanData.shape)

    #plot3D(X, Y, scanData, numy, numx) 

    # adding functionally generated defect to scanData
    yc, xc = [int(n/2) for n in perfectRail.shape] # generating about center of defect
    defX = np.zeros((numy, numx))
    defY = np.zeros((numy, numx))
    
    ny_defect, nx_defect = int(numy/2), int(numx/3) # setting defect size - arbitrary
    a, b, c = nx_defect / 2.0 * dx, ny_defect / 2.0 * dy, .7   # setting ellipsoid params
    
    # setting 'coord' system around defect
    x_maxInd = int(xc + nx_defect/2)
    x_minInd = int(xc - nx_defect/2) 
    y_maxInd = int(yc + ny_defect/2)
    y_minInd = int(yc - ny_defect/2)
    # nx_defect, ny_defect are actually n-1, so if nx_defect = 8, have 9
    # work out better math later, too lazy rn
    
    defX[y_minInd:y_maxInd+1, x_minInd:x_maxInd+1], \
        defY[y_minInd:y_maxInd+1, x_minInd:x_maxInd+1] = \
        np.meshgrid(np.arange(-nx_defect/2, nx_defect/2 + 1) * dx, \
                    np.arange(-ny_defect/2, ny_defect/2 + 1) * dy)  # this works
    
    # generate half-ellipsoid defect about center of rail
    tempZ = (1 - (defX/a)**2 - (defY/b)**2)
    #print(np.around(tempZ, 2))
    if tempZ[yc, xc] == 1: tempZ[yc, xc] = 0.999    # otherwise end up w/ 0 at df center
    tempZ[tempZ == 1] = 0
    tempZ[tempZ < 0] = 0
    #print(np.around(tempZ, 2))
        
    defZ = c**2 * np.sqrt(tempZ)    # gets positive points of an ellipsoid
    #print(np.around(defZ, 2))
    #print(defZ.shape)
    
    scanData = perfectRail - defZ # seems to be working as expected
    
    #plot3D(X, Y, scanData, rcount = numy, ccount = numx)
        
    '''
    not sure if it's better to just subtract off the ellipsoid profile off of
    the 'perfect' profile or to just set the indices to the ellipsoid profile
    -> neither are great, but i'm not sure the best way to do this
    '''
    
    # testing module:
    #ret = interpretData(scanData, dx, dy, sensorHeight, seq=0)

    #print(f"Max Depth: {ret[0]}")
    #print(f"Defect Length: {ret[1]}")
    #print(f"Defect Width: {ret[2]}")
    #print(f"Defect Volume: {ret[3]}")

    # testing all sequences (NOTE: changed return for function for this test to pass back working profile, wp indices)
    # initial scan (seq=0) - milling wp
    wp, dfBounds = interpretData(scanData, dx, dy, sensorHeight, seq=0)
    (rm, rM), (cm, cM) = dfBounds   # unpacking tuple of bounds
    scanData[rm:rM, cm:cM] = wp # updating profile based on new working profile

    # post-milling scan (seq=1) - deposition wp; need to +/- 3 from dfBounds since bounds are for og defect (wp is larger)
    wp, dfBounds = interpretData(scanData, dx, dy, sensorHeight, seq=1)
    (rm, rM), (cm, cM) = dfBounds   # unpacking tuple of bounds
    rm -= 3
    rM += 3
    cm -= 3
    cM += 3
    scanData[rm:rM, cm:cM] = wp # updating profile

    # post-deposition scan (seq=2) - grindout wp
    wp, dfBounds = interpretData(scanData, dx, dy, sensorHeight, seq=2)
    (rm, rM), (cm, cM) = dfBounds   # unpacking tuple of bounds
    scanData[rm:rM, cm:cM] = wp # updating profile based on new working profile

    # post-grinding scan (seq=3) - should just be finished profile
    interpretData(scanData, dx, dy, sensorHeight, seq=3)
    
    
    

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
