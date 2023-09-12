# Plot the newly acquired data from each of the 4 sensors

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Visualisation.Functions.plot_imu_xyz import *


def plot_all_new_data(filepath, title):
    # generate column names
    colNames = ['Frame', 'Time']
    imu_locations = ['lear', 'rear', 'chest', 'pocket']
    repeated_headers = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
    for i in range(0, 4):
        elements = [element + imu_locations[i] for element in repeated_headers]
        colNames.extend(elements)
    # load data from file and call functions for plotting
    data = pd.read_csv(filepath, names=colNames)
    for i in range(0, 4):
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
        plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, title + " " + imu_locations[i])

    plt.tight_layout()
    plt.show()
