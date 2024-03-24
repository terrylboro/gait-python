import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.integrate import cumtrapz
from scipy.signal import butter, filtfilt

# for comparison
from C3d.read_ear_marker import read_ear_marker


def hp_filter(data, freq):
    b, a = butter(2, freq, btype="high", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def calculate_sway(data, time):
    # plt.plot(time, data)
    velocity = cumtrapz(data, time)
    # plt.plot(time[:-1], velocity)
    # plt.show()
    displacement = cumtrapz(hp_filter(velocity, 0.75), time[:-1])
    # displacement = cumtrapz(hp_filter(velocity, 0.5), time[:-1])
    # print(len(displacement))
    # plt.plot(time[:-2], hp_filter(displacement, 0.5) * 100)
    # plt.legend(["Acceleration", "Velocity", "Displacement"])
    # plt.show()
    return displacement

# def get_marker_displacement(subjectPath):




def load_ML_data(filepath):
    return pd.read_csv(filepath, usecols=["AccY"]).to_numpy().flatten()

def main():
    filepath = "../../TiltCorrectedData/TF_57/Walk/Right/"
    markerPath = "C:/Users/teri-/Downloads/A096391_57_0003.c3d"
    for file in os.listdir(filepath):
        if file.endswith("3_NED.csv"):
            data = load_ML_data(filepath + file)
            time = np.linspace(0, len(data)/100, len(data))
            displacement = calculate_sway(hp_filter(data, 0.5), time)
            # plt.plot(hp_filter(displacement[20:], 0.5) / max(hp_filter(displacement[20:], 0.5)))
            # norm_displacement = displacement / np.linalg.norm(displacement)
            norm_displacement = (displacement - np.min(displacement)) / (np.max(displacement) - np.min(displacement))
            plt.plot(norm_displacement[15:])

            # plt.plot(displacement[20:] / max(displacement[20:]))
            mkr_data = read_ear_marker(markerPath)
            # norm_mkr = mkr_data[:, 0] / np.linalg.norm(mkr_data[:, 0])
            norm_mkr = (mkr_data[:, 0] - np.min(mkr_data[:, 0])) / (np.max(mkr_data[:, 0]) - np.min(mkr_data[:, 0]))
            plt.plot(norm_mkr)
            # plt.plot(mkr_data[:, 0] / max(mkr_data[:, 0]))
            plt.legend(["Earable", "Vicon"])
            plt.xlabel("Sample Number (at 100Hz)")
            plt.ylabel("Normalised Side-to-Side Displacement")
            plt.title("Comparison of Sway Displacement from Earable and\nVICON (Gold Standard) During Walking")
            plt.show()

if __name__ == "__main__":
    main()
