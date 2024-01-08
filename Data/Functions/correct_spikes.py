# A function to correct the spikes in the data and also apply filtering

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Visualisation.Functions.plot_imu_xyz import *
from scipy.signal import find_peaks, medfilt
import os

def correct_spikes(loadpath, file, save_path_data, save_path_vis):
    # generate column names
    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/timestampedColumnHeaders", delimiter=',',
                          dtype=str)
    # print(colNames)
    imu_locations = ['lear', 'rear', 'chest', 'pocket']
    # load data from file and call functions for plotting
    data = pd.read_csv(loadpath+file, names=colNames, skiprows=1)
    for i in range(0, 3):
        accel = data[['AccX'+imu_locations[i], 'AccY'+imu_locations[i], 'AccZ'+imu_locations[i]]].values
        gyro = data[['GyroX'+imu_locations[i], 'GyroY'+imu_locations[i], 'GyroZ'+imu_locations[i]]].values
        mag = data[['MagX'+imu_locations[i], 'MagY'+imu_locations[i], 'MagZ'+imu_locations[i]]].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))

        # Start the timestamps relative to zero
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

        # fill in spikes
        for j in range(0, 3):
            mag_peaks, mag_properties = find_peaks(np.square(magReadings[:, j] - np.mean(magReadings[:, j])), height=50)#, threshold=(10, None))
            # print(mag_peaks * 10)
            # print(mag_properties["widths"])
            # plt.figure()
            # plt.plot(range(0,len(magReadings[:, j])), magReadings[:, j] - np.mean(magReadings[:, j]))
            # plt.plot(mag_peaks, magReadings[mag_peaks, j] - np.mean(magReadings[mag_peaks, j]), 'rx')
            # plt.show()
            magReadings[mag_peaks, j] = (magReadings[mag_peaks - 1, j] + magReadings[mag_peaks + 1, j]) / 2
            accelReadings[mag_peaks, j] = (accelReadings[mag_peaks - 1, j] + accelReadings[mag_peaks + 1, j]) / 2
            gyroReadings[mag_peaks, j] = (gyroReadings[mag_peaks - 1, j] + gyroReadings[mag_peaks + 1, j]) / 2

            # assign these values back to the original dataframe
            data[['AccX' + imu_locations[i], 'AccY' + imu_locations[i], 'AccZ' + imu_locations[i]]] = accelReadings
            data[['GyroX' + imu_locations[i], 'GyroY' + imu_locations[i], 'GyroZ' + imu_locations[i]]] = gyroReadings
            data[['MagX' + imu_locations[i], 'MagY' + imu_locations[i], 'MagZ' + imu_locations[i]]] = magReadings


        # print("accel readings: ", accelReadings)
        # print("gyro readings: ", gyroReadings)
        # print("mag readings: ", magReadings)
        # plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file + " " + imu_locations[i])

        # plot_imu_xyz(accelReadings, gyroReadings, np.square(magReadings - np.mean(magReadings, axis=0)), time, file + " " + imu_locations[i])

        # plot_imu_xyz(medfilt(accelReadings), medfilt(gyroReadings), medfilt(magReadings), time,
        #              file + " " + imu_locations[i])
        # plt.tight_layout()
        # plt.show()
        # save the data
        data.to_csv(save_path_data + file, index=False)
        # save the figures
        # plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file + " " + imu_locations[i])
        # plt.savefig(save_path_vis + file.split(".")[0] + imu_locations[i] + ".png")
        # plt.close()


def main():
    # list to loop through for activities
    activities = ["Static"]#["Walk", "WalkShake", "WalkNod", "WalkSlow", "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"]
    # Repeat for all participants
    for i in range(1, 15):
        save_dir_data = "../../FilteredData/Data/TF_" + str.zfill(str(i), 2) + "/"
        save_dir_vis = "../../FilteredData/Visualisation/TF_" + str.zfill(str(i), 2) + "/"
        if not os.path.exists(save_dir_data): os.mkdir(save_dir_data)
        if not os.path.exists(save_dir_vis): os.mkdir(save_dir_vis)
        for activity_name in activities:
            save_path_data = save_dir_data + activity_name + "/"
            save_path_vis = save_dir_vis + activity_name + "/"
            load_path = "../../Data/TF_" + str.zfill(str(i), 2) + "/" + activity_name + "/"
            if not os.path.exists(save_path_data): os.mkdir(save_path_data)
            if not os.path.exists(save_path_vis): os.mkdir(save_path_vis)
            for file in os.listdir(load_path):
                # plot_all_new_data(load_path, file, save_path)
                correct_spikes(load_path, file, save_path_data, save_path_vis)


if __name__ == "__main__":
    main()