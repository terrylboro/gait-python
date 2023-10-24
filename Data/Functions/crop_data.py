# Use this file to crop any new data, making it more amenable to any processign algorithms
# Written by Terry Fawden 13/9/2023

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from Visualisation.Functions.plot_imu_xyz import plot_imu_xyz


def crop_data(load_path, save_path):
    # make the column headers for the dataframe
    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/columnHeaders", delimiter=',',
                          dtype=str)
    # colNames = ['Frame', 'Time']
    # imu_locations = ['lear', 'rear', 'chest', 'pocket']
    # repeated_headers = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
    # for i in range(0, 4):
    #     elements = [element + imu_locations[i] for element in repeated_headers]
    #     colNames.extend(elements)
    # loop through all files in the directory
    for file in os.listdir(load_path):
        data = pd.read_csv(load_path+file, names=colNames)
        accel = data.iloc[:, [2, 3, 4]].values
        gyro = data.iloc[:, [5, 6, 7]].values
        mag = data.iloc[:, [8, 9, 10]].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))

        time = range(0, len(data))
        # time = data['Time'].values
        plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file)
        # Choose cropping location and crop
        startPoint = int(input("Input x value to crop from: "))
        data = data.truncate(before=startPoint)
        # Prepare data for plotting
        accel = data.iloc[:, [2, 3, 4]].values
        gyro = data.iloc[:, [5, 6, 7]].values
        mag = data.iloc[:, [8, 9, 10]].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))
        time = range(startPoint, len(data)+startPoint)
        plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file+" Cropped")
        print(data)
        data.to_csv(save_path+file, index_label="Index")


def crop_ear_data(load_path, save_path):
    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/earColHeaders", delimiter=',',
                          dtype=str)
    for file in os.listdir(load_path):
        if file=="tombrace-3.txt":
            data = pd.read_csv(load_path+file, names=colNames)
            accel = data.iloc[:, [2, 3, 4]].values
            gyro = data.iloc[:, [5, 6, 7]].values
            mag = data.iloc[:, [8, 9, 10]].values
            N = np.size(accel, 0)
            # Rearrange the data to fit the correct format
            accelReadings = np.reshape(accel[:, :], (N, 3))
            gyroReadings = np.reshape(gyro[:, :], (N, 3))
            magReadings = np.reshape(mag[:, :], (N, 3))

            time = range(0, len(data))
            # time = data['Time'].values
            plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file)
            # Choose cropping location and crop
            startPoint = int(input("Input x value to crop from: "))
            data = data.truncate(before=startPoint)
            # Prepare data for plotting
            accel = data.iloc[:, [2, 3, 4]].values
            gyro = data.iloc[:, [5, 6, 7]].values
            mag = data.iloc[:, [8, 9, 10]].values
            N = np.size(accel, 0)
            # Rearrange the data to fit the correct format
            accelReadings = np.reshape(accel[:, :], (N, 3))
            gyroReadings = np.reshape(gyro[:, :], (N, 3))
            magReadings = np.reshape(mag[:, :], (N, 3))
            time = range(startPoint, len(data)+startPoint)
            plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file+" Cropped")
            print(data)
            data.to_csv(save_path+file, index_label="Index")

def main():
    subject = "20231020-tom"
    filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Walk/"
    # Make the directory for saving the cropped data
    savepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/CroppedWalk/"
    try:
        os.mkdir(savepath)
    except OSError:
        print("Directory already exists")
    crop_data(filepath, savepath)
    # for ear only
    # crop_ear_data(filepath, savepath)


if __name__ == "__main__":
    main()
