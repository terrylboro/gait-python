import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

from Visualisation.Functions.plot_imu_xyz import plot_imu_xyz, plot_accel_xyz
from GroundTruths.Functions.load_ground_truth import load_ground_truth_json


def plot_ground_truth(subject, trial, fig, axs):
    df = load_ground_truth_json(subject, trial)
    offset_df = pd.read_csv("../Offsets/TF_" + str(subject).zfill(2) + ".csv")
    offset = offset_df.at[trial, "Offset"]
    print(offset)
    for ax in axs:
        ymin, ymax = ax.get_ylim()
        # LIC, RIC, LTO, RTO
        ax.vlines(df.iloc[0, :] + offset, ymin=ymin, ymax=ymax - 1, color='r', linestyle='solid')
        ax.vlines(df.iloc[1, :] + offset, ymin=ymin, ymax=ymax - 1, color='g', linestyle='solid')
        ax.vlines(df.iloc[2, :] + offset, ymin=ymin, ymax=ymax - 1, color='r', linestyle='dashed')
        ax.vlines(df.iloc[3, :] + offset, ymin=ymin, ymax=ymax - 1, color='g', linestyle='dashed')

def plot_data(subject, trial):
    loaddir = "../../TiltCorrectedData/TF_" + str(subject).zfill(2) + "/"
    side = "Left"
    activity = "Walk/"
    file = loaddir + activity + side + "/TF_" + str(subject).zfill(2) + "-" + str(trial).zfill(2) + "_NED.csv"
    data = pd.read_csv(file)
    print(data.head(2))
    print(file)
    accel = data.loc[:, ['AccX', 'AccY', 'AccZ']].values
    gyro = data.loc[:, ['GyroX', 'GyroY', 'GyroZ']].values
    mag = data.loc[:, ['MagX', 'MagY', 'MagZ']].values
    N = np.size(accel, 0)
    # Rearrange the data to fit the correct format
    accelReadings = np.reshape(accel[:, :], (N, 3))
    gyroReadings = np.reshape(gyro[:, :], (N, 3))
    magReadings = np.reshape(mag[:, :], (N, 3))
    #
    # filtering
    # filteredAccelReadings = filter(accelReadings)
    # filteredGyroReadings = filter(gyroReadings)
    # filteredMagReadings = filter(magReadings)

    time = range(0, len(data))
    fig, axs = plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file + " Unfiltered")
    # plot_imu_xyz(filteredAccelReadings, filteredGyroReadings, filteredMagReadings, time, file + " Filtered")
    # plt.show()
    return fig, axs


def main():
    subject = 8
    for trial in range(3, 6):
        # tsps = load_ground_truth_json(subject, trial)
        fig, axs = plot_data(subject, trial)
        plot_ground_truth(subject, trial, fig, axs)
        plt.show()


if __name__ == "__main__":
    main()
