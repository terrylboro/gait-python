import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from Processing.AccZero.calculate_acc_zero import calculate_acc_zero



def plot_systems_together(subjectRange, activity, accGyro="Acc"):
    for subject in subjectRange:
        goodSubjects = open("../Utils/goodTrials",
                            "r").read()
        if "," + str(subject) + "," in goodSubjects:
            print("Subject: ", subject)
            trialNumDir = "../TiltCorrectedData/TF_{}/{}/Pocket/".format(str(subject).zfill(2), activity)
            trialNums = []
            for file in os.listdir(trialNumDir):
                trialNums.append(file.split("-")[-1][0:2])
            for trialNum in trialNums:
                # try:
                shankData, shankLength, wristData, wristLen = load_shank(subject, trialNum)
                pocketData, pocketLength = load_earable(subject, trialNum, activity, "Pocket")
                chestData, chestLength = load_earable(subject, trialNum, activity, "Chest")
                leftData, leftLength = load_earable(subject, trialNum, activity, "Left")
                rightData, rightLength = load_earable(subject, trialNum, activity, "Right")
                # plt.plot(shankPeaks, shankData.iloc[shankPeaks, 1], 'go')
                # plt.plot(shankData["AccZ"])
                shankData = shankData.iloc[::20, :].reset_index(drop=True)
                wristData = wristData.iloc[::20, :].reset_index(drop=True)

                # find resultant vectors
                if accGyro == "Acc":
                    chestData = calculate_acc_zero(chestData[["AccX", "AccY", "AccZ"]].values)
                    pocketData = calculate_acc_zero(pocketData[["AccX", "AccY", "AccZ"]].values)
                    leftData = calculate_acc_zero(leftData[["AccX", "AccY", "AccZ"]].values)
                    rightData = calculate_acc_zero(rightData[["AccX", "AccY", "AccZ"]].values)
                    shankData = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)
                    wristData = calculate_acc_zero(wristData[["AccX", "AccY", "AccZ"]].values)
                else:
                    chestData = calculate_acc_zero(chestData[["GyroX", "GyroY", "GyroZ"]].values)
                    pocketData = calculate_acc_zero(pocketData[["GyroX", "GyroY", "GyroZ"]].values)
                    leftData = calculate_acc_zero(leftData[["GyroX", "GyroY", "GyroZ"]].values)
                    rightData = calculate_acc_zero(rightData[["GyroX", "GyroY", "GyroZ"]].values)
                    shankData = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)
                    wristData = calculate_acc_zero(wristData[["AccX", "AccY", "AccZ"]].values)

                shankPeaks, _ = find_peaks(shankData, height=50, prominence=10)
                chestPeaks, _ = find_peaks(pocketData, height=20)
                print("Trial: ", trialNum)
                print("Shank Len: ", shankLength / 20)
                print("Chest Len: ", chestLength)
                print(shankPeaks)
                print(chestPeaks)
                print("********")
                # print(chestData.values)
                plt.plot(pocketData / max(pocketData))
                # plt.plot(chestData)
                # plt.plot(leftData)
                # plt.plot(rightData)
                # plt.plot(np.linspace(0, len(shankData) * 20, len(shankData)), calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values))
                plt.plot(shankData/ max(shankData))
                # plt.plot(wristData)
                # plt.plot(chestPeaks, chestData.iloc[chestPeaks, 2], 'bo')
                # plt.plot(shankPeaks, shankData[shankPeaks], 'go')
                plt.legend(["Pocket", "Shank"])
                # plt.plot(shankData)
                plt.show()
                # except:
                #     print("No data for trial: ", trialNum)


def load_shank(subject, trial):
    try:
        filepath = "../WristShankData/TF_{}/TF_{}_{}.csv".format(
            str(subject).zfill(2), str(subject).zfill(2), str(trial).zfill(4))
        wristData = - pd.read_csv(filepath, header=None, usecols=range(0, 6),
                                names=["AccZ", "AccX", "AccY", "GyroZ", "GyroX", "GyroY"])
        shankData = - pd.read_csv(filepath, header=None, usecols=range(6, 12),
                                names=["AccZ", "AccX", "AccY", "GyroZ", "GyroX", "GyroY"])
    except:
        try:
            filepath = "../WristShankData/TF_{}/15_CU_A096391_{}_{}.csv".format(
                str(subject).zfill(2), str(subject).zfill(2), str(trial).zfill(4))
            wristData = pd.read_csv(filepath, header=None, usecols=range(0, 6),
                                    names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
            shankData = pd.read_csv(filepath, header=None, usecols=range(6, 12),
                                    names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
        except:
            try:
                filepath = "../WristShankData/TF_{}/15_CU_A096391_{}_{}.csv".format(
                    str(subject).zfill(2), str(subject).zfill(2), str(subject).zfill(2)+str(trial).zfill(2))
                wristData = pd.read_csv(filepath, header=None, usecols=range(0, 6),
                                        names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
                shankData = pd.read_csv(filepath, header=None, usecols=range(6, 12),
                                        names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
            except:
                try:
                    filepath = "../WristShankData/TF_{}/15_CU_A096391_{}.csv".format(
                        str(subject).zfill(2), str(subject).zfill(2) + str(trial).zfill(2))
                    wristData = pd.read_csv(filepath, header=None, usecols=range(0, 6),
                                            names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
                    shankData = pd.read_csv(filepath, header=None, usecols=range(6, 12),
                                            names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
                except:
                    filepath = "../WristShankData/TF_{}/A096391_{}_{}.csv".format(
                        str(subject).zfill(2), str(subject).zfill(2), str(trial).zfill(4))
                    wristData = pd.read_csv(filepath, header=None, usecols=range(0, 6),
                                            names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
                    shankData = pd.read_csv(filepath, header=None, usecols=range(6, 12),
                                            names=["AccX", "AccZ", "AccY", "GyroX", "GyroZ", "GyroY"])
    return shankData, len(shankData), wristData, len(wristData)


def load_earable(subject, trial, activity, side):
    filepath = "../TiltCorrectedData/TF_{}/{}/{}/TF_{}-{}_NED.csv".format(
        str(subject).zfill(2), activity, side, str(subject).zfill(2), str(trial).zfill(2))
    data = pd.read_csv(filepath, header=0, usecols=["AccX", "AccY", "AccZ"])
    # data = pd.read_csv(filepath, header=0, usecols=["GyroX", "GyroY", "GyroZ"])
    return data, len(data)


def main():
    plot_systems_together(range(49, 50), "Turf2Floor", "Acc")
    # for subject in range(57, 60):
    #     print("Subject: ", subject)
    #     trialNumDir = "../TiltCorrectedData/TF_{}/Walk/Pocket/".format(subject)
    #     trialNums = []
    #     for file in os.listdir(trialNumDir):
    #         trialNums.append(file.split("-")[-1][0:2])
    #     for trialNum in trialNums:
    #         # try:
    #         shankData, shankLength, wristData, wristLen = load_shank(subject, trialNum)
    #         pocketData, pocketLength = load_earable(subject, trialNum, "Walk", "Pocket")
    #         chestData, chestLength = load_earable(subject, trialNum, "Walk", "Chest")
    #         leftData, leftLength = load_earable(subject, trialNum, "Walk", "Left")
    #         rightData, rightLength = load_earable(subject, trialNum, "Walk", "Right")
    #         # plt.plot(shankPeaks, shankData.iloc[shankPeaks, 1], 'go')
    #         # plt.plot(shankData["AccZ"])
    #         shankData = shankData.iloc[::20, :].reset_index(drop=True)
    #         wristData = wristData.iloc[::20, :].reset_index(drop=True)
    #
    #         # find resultant vectors
    #         chestData = calculate_acc_zero(chestData[["AccX", "AccY", "AccZ"]].values)
    #         pocketData = calculate_acc_zero(pocketData[["AccX", "AccY", "AccZ"]].values)
    #         leftData = calculate_acc_zero(leftData[["AccX", "AccY", "AccZ"]].values)
    #         rightData = calculate_acc_zero(rightData[["AccX", "AccY", "AccZ"]].values)
    #         shankData = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)
    #         wristData = calculate_acc_zero(wristData[["AccX", "AccY", "AccZ"]].values)
    #         #
    #         # chestData = calculate_acc_zero(chestData[["GyroX", "GyroY", "GyroZ"]].values)
    #         # pocketData = calculate_acc_zero(pocketData[["GyroX", "GyroY", "GyroZ"]].values)
    #         # leftData = calculate_acc_zero(leftData[["GyroX", "GyroY", "GyroZ"]].values)
    #         # rightData = calculate_acc_zero(rightData[["GyroX", "GyroY", "GyroZ"]].values)
    #         # shankData = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)
    #         # wristData = calculate_acc_zero(wristData[["AccX", "AccY", "AccZ"]].values)
    #
    #         shankPeaks, _ = find_peaks(shankData, height=13)
    #         chestPeaks, _ = find_peaks(chestData, height=13)
    #         print("Trial: ", trialNum)
    #         print("Shank Len: ", shankLength / 20)
    #         print("Chest Len: ", chestLength)
    #         print(shankPeaks)
    #         print(chestPeaks)
    #         print("********")
    #         # print(chestData.values)
    #         plt.plot(pocketData)
    #         # plt.plot(chestData)
    #         # plt.plot(leftData)
    #         # plt.plot(rightData)
    #         # plt.plot(np.linspace(0, len(shankData) * 20, len(shankData)), calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values))
    #         plt.plot(shankData)
    #         # plt.plot(wristData)
    #         # plt.plot(chestPeaks, chestData.iloc[chestPeaks, 2], 'bo')
    #         # plt.plot(shankPeaks, shankData[shankPeaks], 'go')
    #         plt.legend(["Pocket", "Right", "Shank", "Wrist"])
    #         # plt.plot(shankData)
    #         plt.show()
    #         # except:
    #         #     print("No data for trial: ", trialNum)


if __name__ == "__main__":
    main()