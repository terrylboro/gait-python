import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import filtfilt, find_peaks, butter


def filter_wrist(data, freq):
    b, a = butter(2, freq, btype="low", fs=1000, output='ba')
    return filtfilt(b, a, data)


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def process_wrist(data, filter_freq=1.5):
    data = calculate_acc_zero(data)
    data = filter_wrist(data, filter_freq)
    # Find ICs
    ICs, _ = find_peaks(data, prominence=2)
    FCs, _ = find_peaks(-data, prominence=2)
    plt.figure()
    plt.plot(data)
    # plt.plot(ICs, data[ICs], 'x')
    # plt.plot(FCs, data[FCs], 'x')
    return ICs, FCs


def process_wrist_multiple(subjectStart, subjectEnd, activityTypes=["Walk"], saveFig=False):
    # all the subfolders in the "/WristShankData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        for activity in activityTypes:
            loaddir = "../../WristShankData/" + subject + "/" + activity + "/Wrist/"
            image_savedir = "Graphs/" + subject + "/" + activity + "/Wrist/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                acc_data = np.loadtxt(filepath, usecols=range(0, 3), delimiter=",")
                gyro_data = np.loadtxt(filepath, usecols=range(3, 6), delimiter=",")
                acc_ICs, acc_FCs = process_wrist(acc_data, 35)
                # gyro_ICs, gyro_FCs = process_wrist(gyro_data, 1.5)
                plt.title("Wrist Resultant Accelerometer Data")
                plt.xlabel("Time / samples")
                plt.ylabel("Acceleration / m/s^2")
                plt.show()
                plt.close("all")
                # if saveFig:
                #     title = file.split(".")[0] + " " + "Wrist" + " " + "Accelerometer As Scalar"
                #     plt.figure(1)
                #     plt.clf()
                #     plt.plot(np.linspace(0, len(acc_zero_data)/2, len(acc_zero_data)), acc_zero_data)
                #     if mode == "events":
                #         plt.vlines(ICs / 2, 0, 16, colors='r')
                #     plt.title(title)
                #     plt.xlabel("Time / ms")
                #     plt.ylabel(r"Acceleration / $ms^{-2}$")
                #     # plt.show()
                #     if mode == "events":
                #         plt.savefig(events_image_savedir + title)
                #     elif mode == "no_events":
                #         plt.savefig(image_savedir + title)
                #     else:
                #         plt.show()


def main():
    process_wrist_multiple(9, 12)


if __name__ == "__main__":
    main()
