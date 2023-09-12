

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_imu_xyz(accel, gyro, mag, time, title):

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

    fig.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral'], loc='outside upper right')
    fig.suptitle(title, fontsize=18)

    plt.tight_layout()

    plt.show()


def main():
    data = pd.read_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/Tom/tom-2.txt")
    print(data.head())
    accel = data.iloc[:, [2, 3, 4]].values
    gyro = data.iloc[:, [5, 6, 7]].values
    mag = data.iloc[:, [8, 9, 10]].values
    N = np.size(accel, 0)
    # Rearrange the data to fit the correct format
    accelReadings = np.reshape(accel[:, :], (N, 3))
    gyroReadings = np.reshape(gyro[:, :], (N, 3))
    magReadings = np.reshape(mag[:, :], (N, 3))

    temp_accelReadings2 = accelReadings[:, 2]
    accelReadings[:, [1, 2]] = accelReadings[:, [2, 1]]
    accelReadings[:, 2] = - accelReadings[:, 2]
    gyroReadings[:, [1, 2]] = gyroReadings[:, [2, 1]]
    gyroReadings[:, 2] = - gyroReadings[:, 2]
    magReadings[:, [1, 2]] = magReadings[:, [2, 1]]
    magReadings[:, 2] = - magReadings[:, 2]

    time = range(0, len(data))

    plot_imu_xyz(accelReadings, gyroReadings, magReadings, time, "Tom XYZ")

if __name__ == "__main__":
    main()
