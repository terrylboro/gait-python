import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Processing.AccZero.calculate_acc_zero import calculate_acc_zero
from sklearn import preprocessing

from GroundTruths.Functions.load_ground_truth import load_ground_truth_json_new

def normalize(v):
    norm = np.linalg.norm(v, 1)
    if norm == 0:
       return v
    return v / norm

for subjectNum in range(15, 24):
    goodSubjects = open("../../Utils/goodTrials",
                        "r").read()
    if "," + str(subjectNum) + "," in goodSubjects:
        subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
        for file in os.listdir(subjectDir)[4:6]:
            trialNum = int(file.split(".")[0].split("-")[-1])
            data = pd.read_csv(os.path.join(subjectDir, file))
            dataToPlot = data[["AccYlear", "AccZlear", "AccXlear"]]
            plt.plot(dataToPlot)
            # plt.plot(dataToPlot / abs(max(dataToPlot.max().array)))
            wristData = data[["AccXWrist", "AccYWrist", "AccZWrist"]]
            shankData = data[["AccXShank", "AccYShank", "AccZShank"]]
            # normalized_accZero = preprocessing.normalize(calculate_acc_zero(shankData.to_numpy()).reshape(1, len(data)), axis=1)
            normalized_accZero = calculate_acc_zero(shankData.to_numpy()) / np.max(calculate_acc_zero(shankData.to_numpy()))
            # plt.plot(normalized_accZero)
            # load the gt data
            df = load_ground_truth_json_new(subjectNum, trialNum)
            ymin = min(dataToPlot.min().array)
            ymax = max(dataToPlot.max().array)
            # plt.vlines(df.iloc[0, :], ymin=ymin, ymax=ymax, color='r', linestyle='solid')
            # plt.vlines(df.iloc[1, :], ymin=ymin, ymax=ymax, color='g', linestyle='solid')
            plt.vlines(df.iloc[2, :], ymin=ymin, ymax=ymax, color='r', linestyle='dashed')
            plt.vlines(df.iloc[3, :], ymin=ymin, ymax=ymax, color='g', linestyle='dashed')
            plt.title(file)
            plt.show()

