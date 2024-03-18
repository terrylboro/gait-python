import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.integrate import cumtrapz
from scipy.signal import butter, filtfilt


def hp_filter(data, freq):
    b, a = butter(2, freq, btype="high", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def calculate_sway(data, time):
    plt.plot(time, data)
    velocity = cumtrapz(data, time)
    plt.plot(time[:-1], velocity)
    # plt.show()
    displacement = cumtrapz(hp_filter(velocity, 0.5), time[:-1])
    print(len(displacement))
    plt.plot(time[:-2], hp_filter(displacement, 0.5) * 100)
    plt.legend(["Acc", "V", "Displacement"])
    plt.show()




def load_ML_data(filepath):
    return pd.read_csv(filepath, usecols=["AccY"]).to_numpy().flatten()

def main():
    filepath = "../../TiltCorrectedData/NTF_31/WalkNod/Right/"
    for file in os.listdir(filepath):
        data = load_ML_data(filepath + file)
        time = np.linspace(0, len(data)/100, len(data))
        calculate_sway(hp_filter(data, 0.5), time)

if __name__ == "__main__":
    main()
