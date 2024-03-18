import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

from Visualisation.Functions.plot_imu_xyz import plot_imu_xyz, plot_accel_xyz
from GroundTruths.Functions.load_ground_truth import load_ground_truth_json


def plot_ground_truth(subject, trial, fig, axs):
    df = load_ground_truth_json(subject, trial)
    for ax in axs:
        ymin, ymax = ax.get_ylim()
        # LIC, RIC, LTO, RTO
        ax.vlines(df.iloc[0, :], ymin=ymin, ymax=ymax - 1, color='r', linestyle='solid')
        ax.vlines(df.iloc[1, :], ymin=ymin, ymax=ymax - 1, color='g', linestyle='solid')
        ax.vlines(df.iloc[2, :], ymin=ymin, ymax=ymax - 1, color='r', linestyle='dashed')
        ax.vlines(df.iloc[3, :], ymin=ymin, ymax=ymax - 1, color='g', linestyle='dashed')

def plot_data(subject, sides, activities):
    loaddir = "../../TiltCorrectedData/TF_" + str(subject).zfill(2) + "/"
    for side in sides:
        for activity in activities:
            for file in os.listdir(loaddir + activity + "/" + side):
                data = pd.read_csv(loaddir + activity + "/" + side + "/" + file)
                print(data.head(2))
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
    subject = 12
    for trial in range(3, 6):
        # tsps = load_ground_truth_json(subject, trial)
        fig, axs = plot_data(subject, ["Left"], ["Walk"])
        plot_ground_truth(subject, trial, fig, axs)
        plt.show()


if __name__ == "__main__":
    main()
