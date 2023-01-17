# fill this module with the actions taken by the bogey on event (e.g. buttonpress)
# put any other required functions here - these are obvs non extensive


def drive():
    print("figure out something here")

def scanSequence():
    # activate motor to drive scanner mech to other side (until it hits the opposite side)
        # note that have to know which side it needs to move towards

    # trigger scanner data read-in, line-by-line, based on encoder data
        # need to have set dy to know what encoder values to take data readings at
        # store scanner data in some sort of 2D mapping (numpy array or list of tuples possibly)
            # don't worry about dx, dy, as this is handled later - just leave based on indices

    # when scanner hits other side, stop reading in data, and either send scanner back to original side
    # or leave on current side (note that this would mean you have to return the side the scanner is on;
    # this would also add minor complications later on, but in areas beyond the project scope, so, eh)

    scanData = None

    return scanData