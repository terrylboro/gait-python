import os

import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt


def populate_imu_array(itf, sensorNum):
    accX = c3d.get_analog_index(itf, "Sensor {} Acc.ACCX{}".format(sensorNum, sensorNum))
    # print(accX)
    return range(accX, accX+6)

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
    # Get indices using label instead of guessing index
    sensor1Range = populate_imu_array(itf, 1) #range(93, 98+1)
    sensor2Range = populate_imu_array(itf, 2) #range(165, 170+1)
    sensor_arr = np.zeros((end_fr * 20, 12), dtype=np.float32)
    for sig_idx in sensor1Range:
        data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
        sensor_arr[(start_fr-1)*20:, sig_idx - sensor1Range[0]] = data
    for sig_idx in sensor2Range:
        data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
        sensor_arr[(start_fr-1)*20:, sig_idx - sensor2Range[0] + 6] = data

    # sensor_arr = np.empty(((end_fr - start_fr + 1) * 20, 12))
    # Loop through and add all sensor readings to one file
    # for sig_idx in sensor1Range:
    #     data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    #     sensor_arr[:, sig_idx - sensor1Range[0]] = data
    # for sig_idx in sensor2Range:
    #     data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    #     sensor_arr[:, sig_idx - sensor2Range[0] + 6] = data
    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return sensor_arr


def main():
    subjectPath = "C:/Users/teri-/Documents/GaitC3Ds/"
    savePath = "../WristShankData/TF_"
    for subjectDir in os.listdir(subjectPath):
        # find the subject number from the directory name
        subjectNum = subjectDir.split("_")[-1]
        # if int(subjectNum) < 19 and int(subjectNum) > 17:
        if int(subjectNum) in range(23, 45):# and int(subjectNum) not in [0, 2, 3, 4, 5, 11, 16, 38, 46, 47, 48, 54]:
            for trial in os.listdir(subjectPath + subjectDir):
                if trial.endswith(".c3d"):
                    # load the wrist and shank data into a csv
                    print(subjectPath + subjectDir + "/" + trial)
                    sensor_arr = read_c3d(subjectPath + subjectDir + "/" + trial)
                    # print(sensor_arr)
                    print("Saving to: ")
                    print(savePath + subjectNum + "/" + trial.split(".")[0] + ".csv")
                    np.savetxt(savePath + subjectNum + "/" + trial.split(".")[0] + ".csv", sensor_arr, delimiter=",")


if __name__ == "__main__":
    main()
