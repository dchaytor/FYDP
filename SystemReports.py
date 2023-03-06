# GO BACK AND USE MORE DESCRIPTIVE/UNIQUE FILENAMES AT SOME POINT
f = "C:/Users/dunca/OneDrive/Documents/4B/FYDP/FYDP/Reports/"
import time # get rid of this later
from pylatex import Document, Section, Subsection, Figure, SubFigure, NoEscape, Tabular
from pylatex.utils import bold


def repairReport(imgFPs, defectParams, filename='RepairReport', folder = f):
    # NOTE: expecting defectParams to come in as tuple in following order:
    # dfNo, (locLat, locLong), length, width, volume, isRepaired, start time, end time
    dfNo, loc, maxLen, maxWid, vol, isRepaired, tS, tF = defectParams

    fp = folder + filename

    # expecting imgFPs to come in as a list of strings containing FPs to profiles to be plotted
    # order: {sp0, dp0, wp0, sp1, dp1, wp1, sp2, dp2, wp2, sp3}

    g_op = {"tmargin": "1in", "lmargin": "1in"}
    doc = Document(geometry_options=g_op)    # may have to play around with doc options

    with doc.create(Section(f'Analysis Report of Defect #{dfNo}', numbering=False)):  # maybe should put date or something describing which 'run' it is idk   
        doc.append('')

    with doc.create(Subsection('Summary of Defect Parameters:', numbering=False)):
        doc.append(bold('Start time of repair:\t\t'))
        doc.append(f'{tS}\n')
        doc.append(bold('End time of repair:\t\t'))
        doc.append(f'{tF}')

    # putting a table at the start of the report summarizing params (max length, etc)
    doc.append(NoEscape(r'\begin{center}'))
    with doc.create(Tabular('c c c c c', pos='c')) as tb:
        tb.add_row(bold('Location'), bold('Length'), bold('Width'), bold('Volume'), bold('Repair Status'))
        #tb.add_hline()
        tb.add_row(loc, maxLen, maxWid, f"{vol:.2f}", isRepaired)
        #tb.add_hline()
    doc.append(NoEscape(r'\end{center}'))

    # add start time and end time here

    # can't figure out how to get rid of figure labels...
    with doc.create(Subsection('Preliminary Scan:', numbering=False)):
        
        # put images of first scan, isolated defect, proposed mill-out profile here
        with doc.create(Figure(position='h!')) as f:
            f.add_image(fps[0], width = NoEscape(r'.8\linewidth'))
            f.add_caption('Initial scan of rail profile')

        with doc.create(Figure(position='h!')) as f:
            
            with doc.create(SubFigure(position='b',width=NoEscape(r'0.5\linewidth'))) as lf:
                lf.add_image(fps[1], width=NoEscape('\linewidth'))
                lf.add_caption('Identified defect profile')

            with doc.create(SubFigure(position='b',width=NoEscape(r'0.5\linewidth'))) as rf:
                rf.add_image(fps[2], width=NoEscape('\linewidth'))
                rf.add_caption('Proposed milling profile')

            f.add_caption('Recommended defect processing (preliminary state)')
    
    doc.append(NoEscape(r'\pagebreak'))

    with doc.create(Subsection('Post-Milling Scan:', numbering=False)):
        
        # put images of post-mill out scan, isolated ground-out region, proposed material deposition profile here
        with doc.create(Figure(position='h!')) as f:
            f.add_image(fps[3], width = NoEscape(r'.8\linewidth'))
            f.add_caption('Rail profile post-mill out')

        with doc.create(Figure(position='h!')) as f:
            
            with doc.create(SubFigure(position='b',width=NoEscape(r'0.5\linewidth'))) as lf:
                lf.add_image(fps[4], width=NoEscape('\linewidth'))
                lf.add_caption('Milled out profile')

            with doc.create(SubFigure(position='b',width=NoEscape(r'0.5\linewidth'))) as rf:
                rf.add_image(fps[5], width=NoEscape('\linewidth'))
                rf.add_caption('Proposed final weld profile')
            
            f.add_caption('Recommended defect processing (post-milling state)')

    doc.append(NoEscape(r'\pagebreak'))

    with doc.create(Subsection('Post-Deposition Scan:', numbering=False)):
        
        # put images of post-mat'l deposition scan, proposed grinding profile here
        with doc.create(Figure(position='h!')) as f:
            f.add_image(fps[6], width = NoEscape(r'.8\linewidth'))
            f.add_caption('Rail profile post-welding')

        with doc.create(Figure(position='h!')) as f:
            
            with doc.create(SubFigure(position='b',width=NoEscape(r'0.5\linewidth'))) as lf:
                lf.add_image(fps[7], width=NoEscape('\linewidth'))
                lf.add_caption('Weld surface profile')

            with doc.create(SubFigure(position='b',width=NoEscape(r'0.5\linewidth'))) as rf:
                rf.add_image(fps[8], width=NoEscape('\linewidth'))
                rf.add_caption('Proposed grinding profile')
            
            f.add_caption('Recommended defect processing (post-welding state)')

    doc.append(NoEscape(r'\pagebreak'))

    with doc.create(Subsection('Finished Profile:', numbering=False)):
        
        # put images of post-grinding scan (final profile)
        with doc.create(Figure(position='h!')) as f:
            f.add_image(fps[9], width = NoEscape(r'.8\linewidth'))
            f.add_caption('Profile of repaired rail')



    doc.generate_pdf(filepath=fp, clean=True, clean_tex=True)




def shutdownReport(nRepaired, nFailed, startTime, endTime, defectFile="Not Available", folder = f):
    # track total number of defects identified, number repaired, number not repaired,
    # system start time, system end time, system running time, name of file with defect coordinates
    
    nTotal = str(nRepaired + nFailed)

    nRepaired, nFailed = str(nRepaired), str(nFailed)

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
    # no sense adding this unless we add some error handling
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
    '''
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
    '''

    # testing repair report; might be better to pack various params into a list or tuple

    # using params generated from previous tests
    maxLength, maxWidth, maxVol = 7.0, 4.0, 10.17

    # arbitrarily choosing remaining params
    dfRepaired = True
    dfLoc = (2.43145, 5.11251)
    tStart = time.asctime(time.localtime())
    tFin = time.asctime(time.localtime())

    # hardcoding links to generated plots on local drive:
    fps, fd = [], 'C:/Users/dunca/OneDrive/Documents/4B/FYDP/FDR Plots and Reports/'
    for seq in range(0, 3):
        for plot in range(1, 4):
            fps.append(fd + f"seq{seq}_plot0{plot}")
    fps.append(fd + "seq3_plot01")

    rrParams = (1, dfLoc, maxLength, maxWidth, maxVol, dfRepaired, tStart, tFin)

    repairReport(fps, rrParams)

