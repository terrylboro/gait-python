import json
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


def load_events_json(subject, trial):
    # filepath = "../../Processing/Ear/Events/AdaptedDiao/TF_" + str(subject).zfill(2) + ".json"
    filepath = "../../C3d/OwnGroundTruth/RawEvents/TF_" + str(subject).zfill(2) + ".json"
    eventsDict = {}
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    for side in ["left", "right", "chest"]:
        try:
            json_str = json.dumps(data[str(trial).zfill(4)][side])
        except:
            id = str(subject).zfill(2) + str(trial).zfill(2)
            json_str = json.dumps(data[id])
        pd_df = pd.read_json(json_str, orient='index')
        eventsDict[side] = pd_df
    return eventsDict

def load_gt_events_json(subject, trial):
    # filepath = "../../Processing/Ear/Events/AdaptedDiao/TF_" + str(subject).zfill(2) + ".json"
    filepath = "../../C3d/OwnGroundTruth/RawEvents/TF_" + str(subject).zfill(2) + ".json"
    eventsDict = {}
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    for side in ["left", "right", "chest"]:
        try:
            json_str = json.dumps(data[str(trial).zfill(4)][side])
        except:
            id = str(subject).zfill(2) + str(trial).zfill(2)
            json_str = json.dumps(data[id])
        pd_df = pd.read_json(json_str, orient='index')
        eventsDict[side] = pd_df
    return eventsDict


for subjectNum in range(35, 45):
    goodSubjects = open("../../Utils/goodTrials",
                        "r").read()
    if "," + str(subjectNum) + "," in goodSubjects:
        subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
        for file in os.listdir(subjectDir)[4:5]:
            trialNum = int(file.split(".")[0].split("-")[-1])
            data = pd.read_csv(os.path.join(subjectDir, file))
            dataToPlot = data[["AccZrear", "AccZlear", "AccZchest"]]
            # dataToPlot = data[["GyroZShank"]]
            plt.plot(dataToPlot)
            # plt.plot(dataToPlot / abs(max(dataToPlot.max().array)))
            wristData = data[["AccXWrist", "AccYWrist", "AccZWrist"]]
            shankData = data[["AccXShank", "AccYShank", "AccZShank"]]
            # normalized_accZero = preprocessing.normalize(calculate_acc_zero(shankData.to_numpy()).reshape(1, len(data)), axis=1)
            normalized_accZero = calculate_acc_zero(shankData.to_numpy()) / np.max(calculate_acc_zero(shankData.to_numpy()))
            # plt.plot(normalized_accZero)
            # load the gt data
            # df = load_ground_truth_json_new(subjectNum, trialNum)
            eventsDict = load_events_json(subjectNum, trialNum)
            for side, c in zip(["left", "right"], ["r", "g"]):
                df = eventsDict[side]
                ymin = min(dataToPlot.min().array)
                ymax = max(dataToPlot.max().array)
                plt.vlines(df.iloc[0, :], ymin=ymin, ymax=ymax, color=c, linestyle='solid')
                plt.vlines(df.iloc[1, :], ymin=ymin, ymax=ymax, color=c, linestyle='solid')
                plt.vlines(df.iloc[2, :], ymin=ymin, ymax=ymax, color=c, linestyle='dashed')
                plt.vlines(df.iloc[3, :], ymin=ymin, ymax=ymax, color=c, linestyle='dashed')
            plt.title(file)
            plt.show()

