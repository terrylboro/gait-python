import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import json

from Visualisation.Functions.plot_imu_xyz import plot_imu_xyz, plot_accel_xyz
from GroundTruths.Functions.load_ground_truth import load_ground_truth_json, load_ground_truth_json_new


def load_ground_truth_json_aligned_data(subject, trial):
    filepath = "../C3d/OwnGroundTruth/RawEvents/TF_" + str(subject).zfill(2) + ".json"
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    try:
        json_str = json.dumps(data[str(trial).zfill(4)])
    except:
        id = str(subject).zfill(2) + str(trial).zfill(2)
        json_str = json.dumps(data[id])
    pd_df = pd.read_json(json_str, orient='index')
    return pd_df


def plot_ground_truth_new(subject, trial):
    df = load_ground_truth_json_aligned_data(subject, trial)
    # LIC, RIC, LTO, RTO
    plt.vlines(df.iloc[0, :], ymin=5, ymax=15, color='r', linestyle='solid')
    plt.vlines(df.iloc[1, :], ymin=5, ymax=15, color='g', linestyle='solid')
    # ax.vlines(df.iloc[2, :] + offset, ymin=ymin, ymax=ymax - 1, color='r', linestyle='dashed')
    # ax.vlines(df.iloc[3, :] + offset, ymin=ymin, ymax=ymax - 1, color='g', linestyle='dashed')


def main():
    activityList = ["Walk"]
    dataPath = "../TiltCorrectedData/"
    goodSubjects = open("../Utils/goodTrials",
                        "r").read()
    for subjectDir in os.listdir(dataPath):
        subject = int(subjectDir.split("_")[-1])
        if "," + str(subject) + "," in goodSubjects and subject < 58 and subject > 41:
            for activity in activityList:
                for file in os.listdir(dataPath + subjectDir + "/" + activity + "/Right/"):
                    trialNum = int(file.split("-")[-1][0:2])
                    plot_ground_truth_new(subject, trialNum)
                    df = load_ground_truth_json_aligned_data(subject, trialNum)
                    gtSeq = df.T[["LHC", "RHC"]].values.flatten()
                    print(np.diff(gtSeq))
                    if (abs(np.diff(gtSeq)) < 50).any():
                        print(file)
                        print(df.T[["LHC", "RHC"]])
                        data = pd.read_csv("../AlignedData/TF_{}/{}-{}.csv".format(str(subject).zfill(2),
                                                                                      str(subject).zfill(2), str(trialNum).zfill(2)))
                        plt.clf()
                        plt.plot(data[["AccZrear", "AccZlear", "AccZchest"]])
                        plot_ground_truth_new(subject, trialNum)
                        plt.title(file)
                        plt.show()


if __name__ == "__main__":
    main()
