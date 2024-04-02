import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import numpy as np
import pandas as pd
from Alignment.plot_systems_together import load_shank, load_earable
from Processing.AccZero.calculate_acc_zero import calculate_acc_zero


def load_9axis_earable(subject, trial, activity, side):
    filepath = "../TiltCorrectedData/TF_{}/{}/{}/TF_{}-{}_NED.csv".format(
        str(subject).zfill(2), activity, side, str(subject).zfill(2), str(trial).zfill(2))
    data = pd.read_csv(filepath, header=0,
                       usecols=["AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ", "MagX", "MagY", "MagZ"])
    return data

def align_systems(subjectRange, activity):
    for subject in subjectRange:
        print("Subject: ", subject)
        trialNumDir = "../TiltCorrectedData/TF_{}/Walk/Pocket/".format(subject)
        trialNums = []
        for file in os.listdir(trialNumDir):
            trialNums.append(file.split("-")[-1][0:2])
        for trialNum in trialNums:
            isGood = 0
            shankData, shankLength, wristData, wristLen = load_shank(subject, trialNum)
            pocketData, pocketLength = load_earable(subject, trialNum, activity, "Pocket")
            shankData = shankData.iloc[::20, :].reset_index(drop=True)

            # find resultant vectors
            pocketDataAccZero = calculate_acc_zero(pocketData[["AccX", "AccY", "AccZ"]].values)
            shankDataAccZero = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)

            shankPeaks, _ = find_peaks(shankDataAccZero, height=50, prominence=10)
            chestPeaks, _ = find_peaks(pocketDataAccZero, height=20)
            print("Trial: ", trialNum)
            print(shankPeaks)
            print(chestPeaks)
            print("********")

            while isGood != 1:
                # plot normalised values
                plt.plot(pocketDataAccZero / max(pocketDataAccZero))
                plt.plot(shankDataAccZero / max(shankDataAccZero))
                plt.legend(["Pocket", "Shank"])
                plt.show()

                # determine parameters for new file
                array_len = max(shankLength / 20, pocketLength)
                combined_arr = np.zeros((array_len, 49))  # 49 IMU streams
                shiftVal = int(input("Input how far to shift pocket data: "))
                newData = np.roll(pocketDataAccZero, -shiftVal)
                # newData[0:shiftVal] = 0

                # plot rolled values
                plt.close()
                plt.plot(newData / max(newData))
                plt.plot(shankDataAccZero / max(shankDataAccZero))
                plt.legend(["Pocket", "Shank"])
                plt.show()

                isGood = int(input("Good?"))
                if isGood == 1:
                    # Apply the shift to all the IMU streams
                    newPocketData = load_9axis_earable(subject, trialNum, activity, "Pocket")
                    newChestData = load_9axis_earable(subject, trialNum, activity, "Chest")
                    newLeftData = load_9axis_earable(subject, trialNum, activity, "Left")
                    newRightData = load_9axis_earable(subject, trialNum, activity, "Right")
                    newEarableData = np.concatenate((newPocketData, newChestData, newLeftData, newRightData), axis=1)
                    newEarableData = np.roll(newEarableData, -shiftVal)
                    # setup the new array for saving
                    combined_arr[:len(newEarableData), range(0, 36)] = newEarableData
                    print(combined_arr)
                    plt.plot(combined_arr)
                    plt.show()
                    headers = open("../Utils/columnHeaders", "r").read().split(",")[2:]
                    headers.extend([
                                    "AccXWrist", "AccYWrist", "AccXZWrist",
                                    "GyroXWrist", "GyroXWrist", "GyroXWrist"
                                    "AccXShank", "AccYShank", "AccXZShank",
                                    "GyroXShank", "GyroXShank", "GyroXShank"
                                    ])
                    headers = ",".join(headers)
                    print(headers)
                    np.savetxt("newEarableData.txt", newEarableData, delimiter=",", header=headers, fmt="8f")



def main():
    align_systems(range(50, 52), "Walk")


if __name__ == "__main__":
    main()

