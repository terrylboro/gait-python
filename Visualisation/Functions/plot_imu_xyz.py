import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


def plot_imu_xyz(accel, gyro, mag, time, title, legend=["X", "Y", "Z"]):

    fig, axs = plt.subplots(3, sharex=True, layout='constrained')

    # plt.subplot(3, 1, 1)
    axs[0].plot(time, accel[:, 0], 'c-')
    axs[0].plot(time, accel[:, 1], 'm-')
    axs[0].plot(time, accel[:, 2], 'y-')
    axs[0].set(ylabel=r'Acceleration / $ms^{-2}$')

    # plt.subplot(3, 1, 2)
    axs[1].plot(time, gyro[:, 0], 'c-')
    axs[1].plot(time, gyro[:, 1], 'm-')
    axs[1].plot(time, gyro[:, 2], 'y-')
    axs[1].set(ylabel='Angular\n Velocity / $ms^{-1}$')

    # plt.subplot(3, 1, 3)
    axs[2].plot(time, mag[:, 0], 'c-')
    axs[2].plot(time, mag[:, 1], 'm-')
    axs[2].plot(time, mag[:, 2], 'y-')
    axs[2].set(xlabel='Time / samples', ylabel='Magnetic Field\n Strength / uT')

    # Hide x labels and tick labels for all but bottom plot.
    for ax in axs:
        ax.label_outer()

    fig.legend(legend, loc='outside upper right')
    fig.suptitle(title, fontsize=18)

    # plt.tight_layout()
    fig.set_tight_layout(True)

    # plt.show()

def filter(data):
    # means = np.mean(acc_zero_data)
    # acc_zero_data = acc_zero_data - means
    # sos = butter(2, 1.5, btype="low", fs=100, output='sos')
    # filtered_data = sosfilt(sos, acc_zero_data)
    b, a = butter(2, 16, btype="low", fs=100, output='ba')
    filtered_data = filtfilt(b, a, data, padtype=None, axis=0)
    return filtered_data
    # plt.figure()
    # plt.plot(filtered_data)

def plot_multiple(subjectRange, activities, sides):
    for subject in subjectRange:
        loaddir = "../../NEDData/TF_" + str(subject).zfill(2) + "/"
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
                    filteredAccelReadings = filter(accelReadings)
                    filteredGyroReadings = filter(gyroReadings)
                    filteredMagReadings = filter(magReadings)

                    time = range(0, len(data))

                    plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, file+" Unfiltered")
                    plot_imu_xyz(filteredAccelReadings, filteredGyroReadings, filteredMagReadings, time, file+" Filtered")
                    plt.show()




def main():
    plot_multiple(range(22, 24), ["Walk", "WalkNod"], ["Left"])

    # # data = pd.read_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/20231020-tom/"
    # #                    "CroppedWalk/20231020-tom-05.txt")
    # data = pd.read_csv("../../Data/TF_07/Walk/TF_07-07.txt")
    # print(data.head())
    # # pocket
    # # accel = data.iloc[:, [2, 3, 4]].values
    # # gyro = data.iloc[:, [5, 6, 7]].values
    # # mag = data.iloc[:, [8, 9, 10]].values
    # # chest
    # # accel = data.iloc[:, [11, 12, 13]].values
    # # gyro = data.iloc[:, [14, 15, 16]].values
    # # mag = data.iloc[:, [17, 18, 19]].values
    # # lear
    # # accel = data.iloc[:, [20, 21, 22]].values
    # # gyro = data.iloc[:, [23, 24, 25]].values
    # # mag = data.iloc[:, [26, 27, 28]].values
    # # rear
    # # accel = data.iloc[:, [29, 30, 31]].values
    # # gyro = data.iloc[:, [32, 33, 34]].values
    # # mag = data.iloc[:, [35, 36, 37]].values
    #
    # # accel = data.loc[:,['AccXchest', 'AccYchest', 'AccZchest']].values
    # # gyro = data.loc[:,['GyroXchest', 'GyroYchest', 'GyroZchest']].values
    # # mag = data.loc[:,['MagXchest', 'MagYchest', 'MagZchest']].values
    # accel = data.loc[:, ['AccXlear', 'AccYlear', 'AccZlear']].values
    # gyro = data.loc[:, ['GyroXlear', 'GyroYlear', 'GyroZlear']].values
    # mag = data.loc[:, ['MagXlear', 'MagYlear', 'MagZlear']].values
    # # accel = data.loc[:, ['AccXpocket', 'AccYpocket', 'AccZpocket']].values
    # # gyro = data.loc[:, ['GyroXpocket', 'GyroYpocket', 'GyroZpocket']].values
    # # mag = data.loc[:, ['MagXpocket', 'MagYpocket', 'MagZpocket']].values
    #
    # N = np.size(accel, 0)
    # # Rearrange the data to fit the correct format
    # accelReadings = np.reshape(accel[:, :], (N, 3))
    # gyroReadings = np.reshape(gyro[:, :], (N, 3))
    # magReadings = np.reshape(mag[:, :], (N, 3))
    # #
    # # filtering
    # filteredAccelReadings = filter(accelReadings)
    # filteredGyroReadings = filter(gyroReadings)
    # filteredMagReadings = filter(magReadings)
    #
    # time = range(0, len(data))
    #
    # plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, "Unfiltered")
    # plot_imu_xyz(filteredAccelReadings, filteredGyroReadings, filteredMagReadings, time, "Filtered")
    # plt.show()


if __name__ == "__main__":
    main()
