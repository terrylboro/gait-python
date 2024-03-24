import os

import numpy as np
import pyc3dserver as c3d
import pandas as pd


def find_start_frame(filepath):
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    startFrame = itf.GetVideoFrame(0)
    ret = c3d.close_c3d(itf)
    return startFrame


def find_start_frames(subjectPath, savePath):
    for subjectDir in os.listdir(subjectPath):
        offsets = []
        print(subjectDir)
        # find the subject number from the directory name
        subjectNum = subjectDir.split("_")[-1]
        if int(subjectNum) not in [0, 3, 4, 5, 11, 20, 21]:
            for trial in os.listdir(subjectPath + subjectDir):
                if trial.endswith(".c3d"):
                    # load the wrist and shank data into a csv
                    # print(subjectPath + subjectDir + "/" + trial)
                    offset = find_start_frame(subjectPath + subjectDir + "/" + trial)
                    # print("Saving to: ")
                    # print(savePath + subjectNum + "/" + trial.split(".")[0] + ".csv")
                    offsets.append((trial.split(".")[0][-2:], offset))
                    # np.savetxt(savePath + subjectNum + "/" + trial.split(".")[0] + ".csv", sensor_arr, delimiter=",")
        # print(offsets)
        offsets_df = pd.DataFrame(data=offsets, columns=["Trial", "Offset"])
        offsets_df.to_csv(savePath + subjectNum + ".csv", index=False)

def main():
    subjectPath = "C:/Users/teri-/Downloads/transfer_data_240307-20240307T124342Z-001/transfer_data_240307/"
    savePath = "../GroundTruths/Offsets/TF_"
    find_start_frames(subjectPath, savePath)

if __name__ == "__main__":
    main()
