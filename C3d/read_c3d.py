import os

import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt


def read_c3d(filepath):
    """ Extract Wrist and Shank data from c3d and save in """
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    end_fr = itf.GetVideoFrame(1)

    ## Mapping the sensor data to values ########
    # Sensor 1 Acc.X to Gyro.Z = 93 to 98
    # Sensor 2 Acc.X to Gyro.Z = 165 to 170
    ##############################################
    sensor1Range = range(93, 98+1)
    sensor2Range = range(165, 170+1)
    sensor_arr = np.empty(((end_fr - start_fr + 1) * 20, 12))
    # Loop through and add all sensor readings to one file
    for sig_idx in sensor1Range:
        data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
        sensor_arr[:, sig_idx - 93] = data
    for sig_idx in sensor2Range:
        data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
        sensor_arr[:, sig_idx - 165 + 6] = data
    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return sensor_arr


def main():
    subjectPath = "C:/Users/teri-/Downloads/transfer_data_240307-20240307T124342Z-001/transfer_data_240307/"
    savePath = "../WristShankData/TF_"
    for subjectDir in os.listdir(subjectPath):
        # find the subject number from the directory name
        subjectNum = subjectDir.split("_")[-1]
        if int(subjectNum) < 19 and int(subjectNum) > 17:
            for trial in os.listdir(subjectPath + subjectDir):
                if trial.endswith(".c3d"):
                    # load the wrist and shank data into a csv
                    print(subjectPath + subjectDir + "/" + trial)
                    sensor_arr = read_c3d(subjectPath + subjectDir + "/" + trial)
                    print("Saving to: ")
                    print(savePath + subjectNum + "/" + trial.split(".")[0] + ".csv")
                    np.savetxt(savePath + subjectNum + "/" + trial.split(".")[0] + ".csv", sensor_arr, delimiter=",")

if __name__ == "__main__":
    main()
