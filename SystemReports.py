# use python-docx library for creating word docs (google to find library documentation)
# do word doc for repair report, possibly error report; rest just .txt files ok

#from docx import Document   # couldn't find package
# might just write code out for now then test later, install thru windows is a PITA
# maybe look for formats other than docx. just needs text + embedded images

# GO BACK AND USE MORE DESCRIPTIVE/UNIQUE FILENAMES AT SOME POINT


def repairReport():
    print("fill in later")
    # DOING THIS ONE LAST TBH
    # use this to generate repair reports following repair procedure
    # 1 report per repair job; different files in each case
    # use some naming convention with date in name to differentiate

    # show first scan, proposed mill-out profile, post-mill-out scan, post mat'l add scan, final profile

def shutdownReport(nRepaired, nFailed, startTime, endTime, defectFile="Not Available"):
    textOut = "SHUTDOWN REPORT\n~~~~~~~~~~~~~~~\n\n"
    textOut += "Total number of defects analyzed:\t" + nRepaired + nFailed + "\n"
    textOut += "Defects repaired:\t" + nRepaired + "\n"
    textOut += "Defect repairs failed:\t" + nFailed + "\n\n"
    textOut += "System start time:\t" + startTime + "\n"
    textOut += "System end time:\t" + endTime + "\n"
    # might not put system runtime in, not sure yet    
    textOut += "\nFurther details:\t" + defectFile

    with open('ShutdownReport', 'w') as fout:
        fout.write(textOut)
    # report generated in shutdown procedure
    # track total number of defects identified, number repaired, number not repaired,
    # system start time, system end time, system running time, name of file with defect coordinates

#def errorReport():
    #print("fill something in later")
    # report for general errors idk, might get rid of this

def defectReport(defects):
    # expecting tuple array with all defect info (could prob use dictionaries but eh)
    # => order: coordinates, max length/width, repair status, file w/ detailed report 
    # could maybe add a header here as well; check output first then decide

    with open('defectReport', 'w') as fout:
        textOut = "Defect Report:\n~~~~~~~~~~~~~~\n"
        for idx, defect in enumerate(defects, start=1):
            textOut = "\n" + idx
            for item in defect:
                textOut += "\t|\t" + item
            fout.write(textOut)

