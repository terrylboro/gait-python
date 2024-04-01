import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from Processing.AccZero.calculate_acc_zero import calculate_acc_zero



def plot_systems_together():
    print("TODO")


def load_shank(subject, trial):
    try:
        filepath = "../WristShankData/TF_{}/15_CU_A096391_{}_{}.csv".format(
            str(subject).zfill(2), str(subject).zfill(2), str(trial).zfill(4))
        data = pd.read_csv(filepath, header=None, usecols=[0, 1, 2], names=["AccX", "AccZ", "AccY"])
    except:
        try:
            filepath = "../WristShankData/TF_{}/15_CU_A096391_{}_{}.csv".format(
                str(subject).zfill(2), str(subject).zfill(2), str(subject).zfill(2)+str(trial).zfill(2))
            data = pd.read_csv(filepath, header=None, usecols=[0, 1, 2], names=["AccX", "AccZ", "AccY"])
        except:
            try:
                filepath = "../WristShankData/TF_{}/15_CU_A096391_{}.csv".format(
                    str(subject).zfill(2), str(subject).zfill(2) + str(trial).zfill(2))
                data = pd.read_csv(filepath, header=None, usecols=[0, 1, 2], names=["AccX", "AccZ", "AccY"])
            except:
                filepath = "../WristShankData/TF_{}/A096391_{}_{}.csv".format(
                    str(subject).zfill(2), str(subject).zfill(2), str(trial).zfill(4))
                data = pd.read_csv(filepath, header=None, usecols=[0, 1, 2], names=["AccX", "AccZ", "AccY"])
    return data, len(data)


def load_chest(subject, trial, activity, side):
    filepath = "../TiltCorrectedData/TF_{}/{}/{}/TF_{}-{}_NED.csv".format(
        str(subject).zfill(2), activity, side, str(subject).zfill(2), str(trial).zfill(2))
    data = pd.read_csv(filepath, header=0, usecols=["AccX", "AccY", "AccZ"])
    return data, len(data)


def main():
    for subject in range(60, 63):
        print("Subject: ", subject)
        trialNumDir = "../TiltCorrectedData/TF_{}/Walk/Pocket/".format(subject)
        trialNums = []
        for file in os.listdir(trialNumDir):
            trialNums.append(file.split("-")[-1][0:2])
        for trialNum in trialNums:
            # try:
            shankData, shankLength = load_shank(subject, trialNum)
            chestData, chestLength = load_chest(subject, trialNum, "Walk", "Pocket")
            # plt.plot(shankPeaks, shankData.iloc[shankPeaks, 1], 'go')
            # plt.plot(shankData["AccZ"])
            shankData = shankData.iloc[::20, :].reset_index(drop=True)
            # find resultant vector
            chestData = calculate_acc_zero(chestData[["AccX", "AccY", "AccZ"]].values)
            shankData = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)
            shankPeaks, _ = find_peaks(shankData, height=13)
            chestPeaks, _ = find_peaks(chestData, height=13)
            print("Trial: ", trialNum)
            print("Shank Len: ", shankLength / 20)
            print("Chest Len: ", chestLength)
            print(shankPeaks)
            print(chestPeaks)
            print("********")
            # print(chestData.values)
            plt.plot(chestData)
            # plt.plot(np.linspace(0, len(shankData) * 20, len(shankData)), calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values))
            plt.plot(shankData)
            # plt.plot(chestPeaks, chestData.iloc[chestPeaks, 2], 'bo')
            plt.plot(shankPeaks, shankData[shankPeaks], 'go')
            plt.legend(["Pocket", "Shank"])
            # plt.plot(shankData)
            plt.show()
            # except:
            #     print("No data for trial: ", trialNum)


if __name__ == "__main__":
    main()