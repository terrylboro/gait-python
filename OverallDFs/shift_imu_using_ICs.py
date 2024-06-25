import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import argrelmax

gaitCycleDF = pd.read_csv("gaitCycleDetails.csv", usecols=["Subject", "TrialNum", "IC1", "IC3"])
saveDir = "../RealignedOverallDFs/"


def find_array_mode(x: np.array):
    vals, counts = np.unique(x, return_counts=True)
    index = np.argmax(counts)
    return vals[index]


for subjectNum in [x for x in range(10, 68) if x not in [11, 20, 22, 24, 47, 48, 49]]:
    subjectNum2 = str(subjectNum).zfill(2)
    dataDir = "TF_{}/".format(subjectNum2)
    for file in os.listdir(dataDir):
        trialNum = int(file.split('-')[1].split(".")[0])
        print(os.path.join(dataDir, file))
        # load the time series data for this trial
        df = pd.read_csv(os.path.join(dataDir, file))
        # find the peaks for lear and rear IMU (correspond to ICs)
        imuLPeaks = argrelmax(df["AccZLeft"].to_numpy(), order=30)[0]
        imuRPeaks = argrelmax(df["AccZRight"].to_numpy(), order=30)[0]
        # Retrieve the ICs for this trial in a sorted list
        cyclesDF = gaitCycleDF[np.logical_and(gaitCycleDF.Subject == subjectNum, gaitCycleDF.TrialNum == trialNum)]
        opticalPeaks = cyclesDF.IC1.to_numpy()
        opticalPeaks.sort()
        if len(imuLPeaks) >= len(opticalPeaks) and imuLPeaks is not None and opticalPeaks is not None:
            while imuLPeaks[0] < opticalPeaks[0]:
                imuLPeaks = np.delete(imuLPeaks, 0, None)
            # Find the lag between the IMUs and the optical system
            learLagList = np.subtract(imuLPeaks[:len(opticalPeaks)], opticalPeaks)
            rearLagList = np.subtract(imuRPeaks[:len(opticalPeaks)], opticalPeaks)
            x = np.hstack((learLagList, rearLagList)).ravel()
            x = x[x >= 0]
            lag = find_array_mode(x)
            # # plot this to demo the method
            # sns.lineplot(data=df[["AccZLeft", "AccZRight"]])
            # plt.vlines([imuLPeaks], 0, 20, linestyles='dashed')
            # plt.vlines(cyclesDF.IC1.to_list(), 0, 20, linestyles='dashed', colors='red')
            # plt.title(file)
            # plt.show()
            # apply the correction
            colList = ["AccXLeft","AccYLeft","AccZLeft","GyroXLeft","GyroYLeft","GyroZLeft","MagXLeft","MagYLeft","MagZLeft","AccXRight","AccYRight","AccZRight","GyroXRight","GyroYRight","GyroZRight","MagXRight","MagYRight","MagZRight","AccXChest","AccYChest","AccZChest","GyroXChest","GyroYChest","GyroZChest","MagXChest","MagYChest","MagZChest","AccXPocket","AccYPocket","AccZPocket","GyroXPocket","GyroYPocket","GyroZPocket","MagXPocket","MagYPocket","MagZPocket"]
            df[colList] = df[colList].shift(-lag)
            df.to_csv(os.path.join(dataDir, file), index=False)
            # # plot corrected df
            # sns.lineplot(data=df[["AccZLeft", "AccZRight"]])
            # plt.vlines([imuLPeaks], 0, 20, linestyles='dashed')
            # plt.vlines(cyclesDF.IC1.to_list(), 0, 20, linestyles='dashed', colors='red')
            # plt.title(file + " Shifted")
            # plt.show()
        else:
            print("IMU and optical lengths don't line up. Need to skip this one")

