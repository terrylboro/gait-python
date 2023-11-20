# Test code to align the local sensor orientation to the global co-ordinates system

import numpy as np
from scipy.signal import butter, filtfilt
import pandas as pd
import os
import matplotlib.pyplot as plt


def butter_lowpass_filter(data, cutoff, fs, order):
    normal_cutoff = cutoff / (0.5 * fs)
    # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y


def sensor_to_global(data):
    print("Hi")


def main():
    trial_type = "Walk"
    data_path = "../../Data/20231020-tom/" + trial_type + "/"
    # data_path = "../../Data/omar/CroppedWalk/"
    for file in os.listdir(data_path):
        data = pd.read_csv(data_path+file)
        if trial_type == "CroppedWalk":
            data.drop(['Frame'], axis=1, inplace=True)
            data = data[["AccXlear", "AccYlear", "AccZlear"]]
            y = butter_lowpass_filter(data["AccYlear"], 0.2, 100, 2)
            print(np.mean(y))
            print(np.mean(data["AccYlear"]))
        else:
            data = data.iloc[:, [2, 3, 4]]
            plt.plot(data.iloc[:, 1])
            plt.show()
            print(data)
            y = butter_lowpass_filter(data.iloc[:, 1], 1, 100, 2)
            print(np.mean(y))
            print(np.mean(data.iloc[:, 1]))
        plt.plot(y)
        plt.show()


if __name__ == "__main__":
    main()
