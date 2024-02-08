# Plot the newly acquired data from each of the 4 sensors

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Visualisation.Functions.plot_imu_xyz import *
import os


def plot_all_new_data(loadpath, file, save_path):
    # generate column names
    colNames = ['Frame', 'Time']
    imu_locations = ['lear', 'rear', 'chest', 'pocket']
    repeated_headers = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
    for i in range(0, 4):
        elements = [element + imu_locations[i] for element in repeated_headers]
        colNames.extend(elements)
    # load data from file and call functions for plotting
    data = pd.read_csv(loadpath+file, names=colNames)
    for i in range(0, 3):
        accel = data.iloc[:, [9 * i + 2, 9 * i + 3, 9 * i + 4]].values
        gyro = data.iloc[:, [9 * i + 5, 9 * i + 6, 9 * i + 7]].values
        mag = data.iloc[:, [9 * i + 8, 9 * i + 9, 9 * i + 10]].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))

        accelReadings[:, [1, 2]] = accelReadings[:, [2, 1]]
        accelReadings[:, 2] = - accelReadings[:, 2]
        gyroReadings[:, [1, 2]] = gyroReadings[:, [2, 1]]
        gyroReadings[:, 2] = - gyroReadings[:, 2]
        magReadings[:, [1, 2]] = magReadings[:, [2, 1]]
        magReadings[:, 2] = - magReadings[:, 2]

        # time = range(0, len(data))
        time = data['Time'].values - data['Time'].values[0]
        # print("accel readings: ", accelReadings)
        # print("gyro readings: ", gyroReadings)
        # print("mag readings: ", magReadings)
        plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file + " " + imu_locations[i])
        plt.savefig(save_path + file.split(".")[0] + imu_locations[i] + ".png")
        plt.close()

def plot_all_new_data_timestamped(loadpath, file, save_path):
    # generate column names
    # colNames = ['Frame', 'AccTimeA', 'AccTimeB', 'MagTimeA', 'MagTimeB', 'AccTimeC', 'AccTimeD', 'MagTimeC', 'MagTimeD']
    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/timestampedColumnHeaders", delimiter=',',
                          dtype=str)
    # print(colNames)
    imu_locations = ['lear', 'rear', 'chest', 'pocket']
    # repeated_headers = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
    # for i in range(0, 4):
    #     elements = [element + imu_locations[i] for element in repeated_headers]
    #     colNames.extend(elements)
    # load data from file and call functions for plotting
    data = pd.read_csv(loadpath+file, names=colNames, skiprows=1)
    for i in range(0, 4):
        # accel = data.iloc[:, [9 * i + 2, 9 * i + 3, 9 * i + 4]].values
        # gyro = data.iloc[:, [9 * i + 5, 9 * i + 6, 9 * i + 7]].values
        # mag = data.iloc[:, [9 * i + 8, 9 * i + 9, 9 * i + 10]].values
        accel = data[['AccX'+imu_locations[i], 'AccY'+imu_locations[i], 'AccZ'+imu_locations[i]]].values
        gyro = data[['GyroX'+imu_locations[i], 'GyroY'+imu_locations[i], 'GyroZ'+imu_locations[i]]].values
        mag = data[['MagX'+imu_locations[i], 'MagY'+imu_locations[i], 'MagZ'+imu_locations[i]]].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))

        # accelReadings[:, [1, 2]] = accelReadings[:, [2, 1]]
        # accelReadings[:, 2] = - accelReadings[:, 2]
        # gyroReadings[:, [1, 2]] = gyroReadings[:, [2, 1]]
        # gyroReadings[:, 2] = - gyroReadings[:, 2]
        # magReadings[:, [1, 2]] = magReadings[:, [2, 1]]
        # magReadings[:, 2] = - magReadings[:, 2]

        # time = range(0, len(data))
        if i == 0:
            time = data['AccCTime'].values - data['AccCTime'].values[0]
        elif i == 1:
            time = data['AccDTime'].values - data['AccDTime'].values[0]
        elif i == 2:
            time = data['AccATime'].values - data['AccATime'].values[0]
        elif i == 3:
            time = data['AccBTime'].values - data['AccBTime'].values[0]
        else:
            print("Out of bounds")

        # print("accel readings: ", accelReadings)
        # print("gyro readings: ", gyroReadings)
        # print("mag readings: ", magReadings)
        plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file + " " + imu_locations[i])
        # plt.tight_layout()
        plt.savefig(save_path + file.split(".")[0] + imu_locations[i] + ".png")
        plt.close()

    # plt.tight_layout()
    # plt.savefig(save_path+file)


def plot_all_new_data_timestamped(loadpath, file, save_path):
    # generate column names
    # colNames = ['Frame', 'AccTimeA', 'AccTimeB', 'MagTimeA', 'MagTimeB', 'AccTimeC', 'AccTimeD', 'MagTimeC', 'MagTimeD']
    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/timestampedColumnHeaders", delimiter=',',
                          dtype=str)
    # print(colNames)
    imu_locations = ['lear', 'rear', 'chest', 'pocket']
    # repeated_headers = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
    # for i in range(0, 4):
    #     elements = [element + imu_locations[i] for element in repeated_headers]
    #     colNames.extend(elements)
    # load data from file and call functions for plotting
    data = pd.read_csv(loadpath+file, names=colNames, skiprows=1)
    for i in range(0, 4):
        # accel = data.iloc[:, [9 * i + 2, 9 * i + 3, 9 * i + 4]].values
        # gyro = data.iloc[:, [9 * i + 5, 9 * i + 6, 9 * i + 7]].values
        # mag = data.iloc[:, [9 * i + 8, 9 * i + 9, 9 * i + 10]].values
        accel = data[['AccX'+imu_locations[i], 'AccY'+imu_locations[i], 'AccZ'+imu_locations[i]]].values
        gyro = data[['GyroX'+imu_locations[i], 'GyroY'+imu_locations[i], 'GyroZ'+imu_locations[i]]].values
        mag = data[['MagX'+imu_locations[i], 'MagY'+imu_locations[i], 'MagZ'+imu_locations[i]]].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))

        # accelReadings[:, [1, 2]] = accelReadings[:, [2, 1]]
        # accelReadings[:, 2] = - accelReadings[:, 2]
        # gyroReadings[:, [1, 2]] = gyroReadings[:, [2, 1]]
        # gyroReadings[:, 2] = - gyroReadings[:, 2]
        # magReadings[:, [1, 2]] = magReadings[:, [2, 1]]
        # magReadings[:, 2] = - magReadings[:, 2]

        # time = range(0, len(data))
        if i == 0:
            time = data['AccCTime'].values - data['AccCTime'].values[0]
        elif i == 1:
            time = data['AccDTime'].values - data['AccDTime'].values[0]
        elif i == 2:
            time = data['AccATime'].values - data['AccATime'].values[0]
        elif i == 3:
            time = data['AccBTime'].values - data['AccBTime'].values[0]
        else:
            print("Out of bounds")

        # print("accel readings: ", accelReadings)
        # print("gyro readings: ", gyroReadings)
        # print("mag readings: ", magReadings)
        plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file + " " + imu_locations[i])
        # plt.tight_layout()
        plt.savefig(save_path + file.split(".")[0] + imu_locations[i] + ".png")
        plt.close()

def main():
    # individual files
    # filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/Iwan/Walk/iwan-7.txt"
    # title = "data visualised"
    # plot_all_new_data(filepath, title)
    # cycle through folder
    # subject = "TF_06"
    # load_path = "../../Data/TF_06/Walk/"
    # save_path = "../../Visualisation/"+subject+"/"
    # list to loop through for activities
    activities = ["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow", "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"]
    # Repeat for all participants
    for i in range(20, 21):
        try:
            os.mkdir("../../Visualisation/TF_" + str.zfill(str(i), 2) + "/")
        except OSError:
            print("Folder already exists!")
        for activity_name in activities:
            save_path = "../../Visualisation/TF_" + str.zfill(str(i), 2) + "/" + activity_name + "/"
            load_path = "../../Data/TF_" + str.zfill(str(i), 2) + "/" + activity_name + "/"
            try:
                os.mkdir(save_path)
            except OSError:
                print("Folder already exists!")
            for file in os.listdir(load_path):
                # plot_all_new_data(load_path, file, save_path)
                plot_all_new_data_timestamped(load_path, file, save_path)


if __name__ == "__main__":
    main()

