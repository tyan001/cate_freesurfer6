#print("-------------run runin-maker.py----------------")
import logging
from os import listdir
import csv
import getpass

#initialise log file
logging.basicConfig( filename="runin-maker.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s",)
logging.info(getpass.getuser() + " started runin-maker.py")

#initialising the CSV writer
runin = open('./run.in','w')
#writer = csv.writer(runin)

#listing the MRI and PET directories into arrays
MR_filelist = listdir("./MRI/")
PT_filelist = listdir("../nii/")


#Arrays to track elements with no matchups
lonelyPT= []
lonelyMR= []
lonelyMR_flag = [0 for i in range(len(MR_filelist))] # array matching the MRI file list to flag if a scan is matched at least once

# For each file name in the ./PET/ directory, extract the ID and find matches in the ./MRI/ directory
for i in range(0, len(PT_filelist)):
    ptC = 0 # flag to determine if a PET gets matched
    currPT = PT_filelist[i]
    currPT = str(currPT.split(".nii")[0]) # Pruning .nii file extension for compatibility with mergeTables.py
    logging.info("Currently working on: " + currPT)
    PT_ID = (currPT.split("-")[2]) #extracting the ID based on - delimeters
    print(PT_ID)
    #Go through list of MRs and extract the ID to match up with the current PET file being checked
    for j in range(0, len(MR_filelist)):
        currMR = MR_filelist[j]
        #MR_ID = (currMR.split("-")[2] + "-" + currMR.split("-")[3] ) # extracting the ID based on '-' delimeters
        MR_ID = (currMR.split("-")[2])
        print (PT_ID + " and " + MR_ID)
        #Add the pair to the run.in if they are a match
        if (MR_ID == PT_ID):
            runin.write(str(currPT)+ ","+str(currMR)+"\n")
            ptC = 1 # flag currPT being matched
            lonelyMR_flag[j] = 1
    if ptC == 0: # Mark unmatched PETs
        lonelyPT.append(PT_filelist[i])

runin.close() #closing writer for the csv 

for i in range(len(lonelyMR_flag)):
    if lonelyMR_flag[i] == 0:
        lonelyMR.append(MR_filelist[i])

# Mistmatch warning to user
if (len(lonelyPT) != 0):
    logging.warning('The following PETs did not have a match:\n\t\t\t\t\t\t\t\t' + ('\n\t\t\t\t\t\t\t\t'.join(map(str, lonelyPT))))
    print("1 or more PET(s) were unable to be matched.\nCheck runin-maker.log for more information")
    
if (len(lonelyMR) != 0):
    logging.warning('The following MRIs did not have a match:\n\t\t\t\t\t\t\t\t' + ('\n\t\t\t\t\t\t\t\t'.join(map(str, lonelyMR))))
    print("1 or more MRI(s) were unable to be matched.\nCheck runin-maker.log for more information")
    
logging.info("runin-maker.py end\n")
#print("-------------end runin-maker.py----------------")
