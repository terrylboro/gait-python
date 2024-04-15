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
        saveDir = "../AlignedData/TF_{}/".format(str(subject).zfill(2))
        trialNumDir = "../TiltCorrectedData/TF_{}/{}/Pocket/".format(str(subject).zfill(2), activity)
        trialNums = []
        for file in os.listdir(trialNumDir):
            trialNums.append(file.split("-")[-1][0:2])
        for trialNum in trialNums:
            isGood = 0
            shankData, shankLength, wristData, wristLen = load_shank(subject, trialNum)
            pocketData, pocketLength = load_earable(subject, trialNum, activity, "Pocket")
            shankData = shankData.iloc[::20, :].reset_index(drop=True)
            wristData = wristData.iloc[::20, :].reset_index(drop=True)

            # find resultant vectors
            pocketDataAccZero = calculate_acc_zero(pocketData[["AccX", "AccY", "AccZ"]].values)
            shankDataAccZero = calculate_acc_zero(shankData[["AccX", "AccY", "AccZ"]].values)

            shankPeaks, _ = find_peaks(shankDataAccZero, height=50, prominence=10)
            chestPeaks, _ = find_peaks(pocketDataAccZero, height=20)
            print("Trial: ", trialNum)
            print("********")

            while isGood != 1:
                # plot normalised values
                plt.plot(pocketDataAccZero / max(pocketDataAccZero))
                plt.plot(shankDataAccZero / max(shankDataAccZero))
                plt.legend(["Pocket", "Shank"])
                plt.show()

                # determine parameters for new file
                array_len = int(max(shankLength / 20, pocketLength))
                combined_arr = np.zeros((array_len, 48))  # 48 IMU streams
                shiftVal = int(input("Input how far to shift pocket data: "))
                if len(pocketDataAccZero) < array_len:
                    pocketDataAccZero = np.pad(pocketDataAccZero, (0, array_len - pocketLength))
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
                    newEarableData = np.zeros((len(newRightData) - shiftVal, 36))
                    if shiftVal >= 0:
                        newEarableData = np.concatenate((newLeftData.loc[shiftVal:, :], newRightData.loc[shiftVal:, :], newChestData.loc[shiftVal:, :], newPocketData.loc[shiftVal:, :]), axis=1)
                    else:
                        newEarableData[shiftVal:, :] = np.concatenate((newLeftData, newRightData, newChestData, newPocketData), axis=1)
                    # newEarableData = np.roll(newEarableData, -shiftVal)
                    # setup the new array for saving
                    # newEarableData[0:shiftVal, :] = 0  # firstly, we want to set the rolled values to zero
                    combined_arr[:len(newEarableData), range(0, 36)] = newEarableData
                    # add in the shank and wrist
                    combined_arr[:int(shankLength / 20), range(36, 48)] = np.concatenate((shankData, wristData), axis=1)
                    # check this looks ok
                    plt.close()
                    plt.plot(shankData)
                    plt.show()
                    # then format the headers to match the columns
                    headers = open("../Utils/columnHeaders", "r").read().split(",")[2:]
                    headers.extend([
                        "AccXShank", "AccYShank", "AccZShank",
                        "GyroXShank", "GyroYShank", "GyroZShank",
                        "AccXWrist", "AccYWrist", "AccZWrist",
                        "GyroXWrist", "GyroYWrist", "GyroZWrist"
                    ])
                    headers = ",".join(headers)
                    plt.close("all")
                    # save to a file
                    np.savetxt(saveDir + "{}-{}.csv".format(str(subject).zfill(2), trialNum), combined_arr, delimiter=",", header=headers, fmt="%2.8f", comments='')


def main():
    align_systems(range(49, 50), "Floor2Turf")


if __name__ == "__main__":
    main()

