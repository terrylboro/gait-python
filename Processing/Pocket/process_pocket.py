import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import filtfilt, find_peaks, butter, argrelextrema


def filter_pocket(data, freq):
    b, a = butter(2, freq, btype="low", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def process_pocket(data, filter_freq=1.5):
    # data = calculate_acc_zero(data)
    data = filter_pocket(data, filter_freq)
    p, h = plot_vertical_component(data)
    # Find ICs
    ICs = []
    FCs = []
    # Define ICs as local minimum before the big vertical loading peak
    stance_peaks, _ = find_peaks(p, prominence=6)
    print(stance_peaks)
    for peak in stance_peaks:
        mins_before_stance = argrelextrema(p[range(peak-8, peak)], np.less)[0]
        if len(mins_before_stance) > 0:
            # pick local min closest to stance
            IC = peak - (8 - mins_before_stance[-1])
        else:
            # This means there is no local min, so pick point with lowest gradient
            IC = peak - (8 - np.argmin(np.diff(p[range(peak-8, peak)])))
        ICs.append(IC)
        # FCs.append(argrelextrema(p[range(peak, peak+10)], np.less)[0])
    print(ICs)
    plt.figure()
    plt.plot(p)
    plt.plot(ICs, p[ICs], 'x')
    plt.plot(FCs, p[FCs], 'x')
    return ICs, FCs


def plot_vertical_component(data):
    acc_zero_data = calculate_acc_zero(data)
    gravity = np.mean(data, axis=0)
    d = data - gravity
    # projection, p of d in vertical axis v
    gravity_dot = np.dot(gravity, gravity)
    gravity_norm = np.linalg.norm(gravity)
    # p = np.ones_like(d)
    p = np.ones(len(data))
    h = np.ones(len(data))
    for i in range(0, len(d)):
        p[i] = (np.dot(d[i, :], gravity)) / gravity_norm
        h[i] = np.linalg.norm(d[i, :] - (np.dot(d[i, :], gravity)) / gravity_dot * gravity)
        # p[i] = (np.dot(d[i, :], gravity)) / gravity_dot * gravity
    # p = (np.dot(d, gravity) / np.dot(gravity, gravity)) * gravity
    # plt.plot(range(0, len(data)), filter_pocket(np.linalg.norm(p, axis=1), 15))
    # print(p)
    # plt.plot(range(0, len(data)), filter_pocket(p, 20))
    # # plt.plot(range(0, len(data)), np.linalg.norm(d-p, axis=1))
    # plt.plot(filter_pocket(-data[:, 2] - np.mean(-data[:, 2] ), 10))
    # plt.plot(-data[:, 2] - np.mean(-data[:, 2]))
    # plt.plot(range(0, len(data)), filter_pocket(h, 10))
    # plt.plot(range(0, len(data)), filter_pocket(acc_zero_data - np.mean(acc_zero_data, axis=0), 15))
    # plt.legend(["p", "h", "Acc_zero"])
    # plt.plot(range(0, len(data)), d)

    # plt.plot(range(0, len(data)), gravity)
    # plt.show()
    return p, h


def process_pocket_multiple(subjectStart, subjectEnd, activityTypes=["Walk"], saveFig=False):
    # all the subfolders in the "/PocketShankData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        for activity in activityTypes:
            loaddir = "../../NEDData/" + subject + "/" + activity + "/Pocket/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                # acc_data = np.loadtxt(filepath, usecols=range(1, 4), delimiter=",")
                acc_data = pd.read_csv(filepath, usecols=['AccX', 'AccY', 'AccZ']).values
                # plot_vertical_component(acc_data)
                process_pocket(acc_data, 20)
                # acc_ICs, acc_FCs = process_pocket(acc_data, 25)
                plt.show()
                plt.close("all")
                # if saveFig:
                #     title = file.split(".")[0] + " " + "Pocket" + " " + "Accelerometer As Scalar"
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
    process_pocket_multiple(7, 18, ["Walk"])


if __name__ == "__main__":
    main()
