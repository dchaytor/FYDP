# use python-docx library for creating word docs (google to find library documentation)
# do word doc for repair report, possibly error report; rest just .txt files ok

#from docx import Document   # couldn't find package
# might just write code out for now then test later, install thru windows is a PITA
# maybe look for formats other than docx. just needs text + embedded images

# GO BACK AND USE MORE DESCRIPTIVE/UNIQUE FILENAMES AT SOME POINT
f = "C:/Users/dunca/OneDrive/Documents/4B/FYDP/FYDP/Reports/"
import time # get rid of this later


def repairReport():
    print("fill in later")
    # DOING THIS ONE LAST TBH
    # use this to generate repair reports following repair procedure
    # 1 report per repair job; different files in each case
    # use some naming convention with date in name to differentiate

    # show first scan, proposed mill-out profile, post-mill-out scan, post mat'l add scan, final profile

def shutdownReport(nRepaired, nFailed, startTime, endTime, defectFile="Not Available", folder = f):
    # track total number of defects identified, number repaired, number not repaired,
    # system start time, system end time, system running time, name of file with defect coordinates
    
    nTotal = str(nRepaired + nFailed)

    nRepaired, nFailed = str(nRepaired), str(nFailed)


    #textOut = "SHUTDOWN REPORT\n~~~~~~~~~~~~~~~\n\n"
    textOut = "SHUTDOWN REPORT:\n\n"
    textOut += "Total number of defects analyzed:\t" + nTotal + "\n"
    textOut += "Defects repaired:\t" + nRepaired + "\n"
    textOut += "Defect repairs failed:\t" + nFailed + "\n\n"
    textOut += "System start time:\t" + startTime + "\n"
    textOut += "System end time:\t" + endTime + "\n"
    textOut += "\nFurther details available in:\t" + defectFile

    with open(folder + 'ShutdownReport', 'w') as fout:
        fout.write(textOut)
    

def errorReport(errorCodes, folder = f):
    # report to store any exceptions raised in code while running
    # expects a list of tuples with the time an error occured and an error message

    if not type(errorCodes) == list:
        pass


def defectReport(defects, folder = f):
    # expecting tuple list with all defect info (could prob use dictionaries but eh)
    # => order: coordinates, max length/width, repair status, file w/ detailed report

    rp = 25 # right padding to add

    fp = folder + 'DefectReport'

    with open(fp, 'w') as fout:
        #textOut = "Defect Report:\n~~~~~~~~~~~~~~\n"
        textOut = "Defect Report:\n\n"
        textOut += "No".ljust(10) + "Coordinates".ljust(rp) + "Max Length".ljust(rp) \
            + "Max Width".ljust(rp) + "Repair Status".ljust(rp) + "Report File"
        for idx, defect in enumerate(defects, start=1):
            textOut += "\n" + str(idx).ljust(10)

            for item in defect:
                textOut += str(item).ljust(rp)

        (fout.write(textOut))
    return fp

if __name__ == "__main__":
    # testing report outputs
    
    dummy_defects = [
        ((2.43145, 5.11251), 10, 2, True, "test1.txt"),
        ((5.88919, 10.12312), 10, 2, True, "test2.txt"),
        ((10.01980, 3.33324), 10, 2, False, "test3.txt")
    ]
    
    defectFP = defectReport(dummy_defects, f)

    nRepaired, nFailed = 3, 1
    startTime = time.asctime(time.localtime())
    time.sleep(2)  # just so starttime and endtime are different; will prob get rid of this
    endTime = time.asctime(time.localtime())
    shutdownReport(nRepaired, nFailed, startTime, endTime, defectFP, f)
    #print(type(startTime))  # string
    #print(startTime)

