# A script to correct for the offset of the IMUs on the headset and align
# their directions with the global co-ordinates system
# Written by Terry Fawden 8/2/2024

import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from scipy.signal import filtfilt, butter


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def plot_vertical_component(data):
    gravity = np.mean(data, axis=0)
    print(gravity)
    d = data - gravity
    print(len(d))
    # projection, p of d in vertical axis v
    gravity_dot = np.dot(gravity, gravity)
    gravity_norm = np.linalg.norm(gravity)
    # p = np.ones_like(d)
    p = np.ones(len(data))
    h = np.ones(len(data))
    for i in range(0, len(d)):
        p[i] = (np.dot(d[i, :], gravity)) / gravity_norm
        h[i] = np.linalg.norm(d[i, :] - (np.dot(d[i, :], gravity)) / gravity_dot * gravity)
    print(p.shape)
    return p, h


def filter_trial(data, freq):
    b, a = butter(2, freq, btype="low", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)


def tilt_correct(data, acc_zero):
    gravity = np.mean(data, axis=0)
    true_gravity = np.array([0., 0., acc_zero])
    # apply vertical correction in 2D
    print(gravity[1:3])
    print([0., np.mean(acc_zero)])
    tilt_dot = np.dot(gravity[1:3] / np.linalg.norm(gravity[1:3]), [0., np.mean(acc_zero)]/ np.linalg.norm(np.mean(acc_zero)))
    tilt_angle = np.arccos(tilt_dot)
    print(tilt_angle)
    # norm_x = AccX / np.linalg.norm(AccX)
    # norm_y = AccY / np.linalg.norm(AccY)
    # norm_z = AccZ / np.linalg.norm(AccZ)
    # plt.plot(norm_x)
    # plt.plot(norm_y)
    # plt.plot(norm_z)

    plt.show()


def tilt_correct_multiple(subjectStart, subjectEnd):
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        sides = ["Left", "Right"]
        for side in sides:
            loaddir = "../../NEDData/" + subject + "/Static/" + side + "/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                acc_data = pd.read_csv(filepath, usecols=['AccX', 'AccY', 'AccZ']).values
                # find the resultant vector
                acc_zero = calculate_acc_zero(acc_data)
                p, _ = plot_vertical_component(acc_data)
                # apply low pass filtering
                # acc_data = filter_trial(acc_data, 0.1)
                # filtered_acc_zero = filter_trial(acc_zero, 0.1)
                plt.plot(acc_zero)
                # plt.plot(range(0, len(p)), p)
                plt.plot(acc_data)
                plt.title(file + " " + side)
                plt.legend(["Resultant", "X", "Y", "Z"])
                plt.show()
                tilt_correct(acc_data, acc_zero)


def main():
    tilt_correct_multiple(1, 21)



if __name__ == "__main__":
    main()

