import os
import pyc3dserver as c3d
import numpy as np
import pandas as pd

def get_offset(filepath):
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    ret = c3d.close_c3d(itf)
    return start_fr

def main():
    subjectPath = "C:/Users/teri-/Documents/GaitC3Ds/"
    goodSubjects = open("../Utils/goodTrials",
                        "r").read()
    offsets = []
    for subject in os.listdir(subjectPath)[-3:]:
        print(subject)
        # if "," + str(subject.split("_")[1]).zfill(2) + "," in goodSubjects:
        subjectNum = int(str(subject.split("_")[1]))
        filepath = subjectPath + subject + "/"
        for file in os.listdir(filepath):
            if file.endswith(".c3d"):
                trialNum = int(file.split('_')[-1].split(".")[0])
                offset = get_offset(filepath + file)
                offsets.append([subjectNum, trialNum, offset])

    df = pd.DataFrame(offsets, columns=['Subject', 'Trial', 'Offset'])
    df.to_csv("offsets.csv", index=False)


if __name__ == "__main__":
    main()
