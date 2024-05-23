import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import filtfilt, find_peaks, butter


def filter_wrist(data, freq):
    b, a = butter(2, freq, btype="low", fs=1000, output='ba')
    return filtfilt(b, a, data)


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def process_wrist(data, filter_freq=1.5):
    data = calculate_acc_zero(data)
    data = filter_wrist(data, filter_freq)
    # Find ICs
    ICs, _ = find_peaks(data, prominence=2)
    FCs, _ = find_peaks(-data, prominence=2)
    plt.figure()
    plt.plot(data)
    # plt.plot(ICs, data[ICs], 'x')
    # plt.plot(FCs, data[FCs], 'x')
    return ICs, FCs


def process_wrist_multiple(subjectStart, subjectEnd, activityTypes=["Walk"], saveFig=False):
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        for activity in activityTypes:
            loaddir = "../../WristShankData/" + subject + "/" + activity + "/Wrist/"
            image_savedir = "Graphs/" + subject + "/" + activity + "/Wrist/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                acc_data = np.loadtxt(filepath, usecols=range(0, 3), delimiter=",")
                gyro_data = np.loadtxt(filepath, usecols=range(3, 6), delimiter=",")
                acc_ICs, acc_FCs = process_wrist(acc_data, 35)
                # gyro_ICs, gyro_FCs = process_wrist(gyro_data, 1.5)
                plt.title("Wrist Resultant Accelerometer Data")
                plt.xlabel("Time / samples")
                plt.ylabel("Acceleration / m/s^2")
                plt.show()
                plt.close("all")
                # if saveFig:
                #     title = file.split(".")[0] + " " + "Wrist" + " " + "Accelerometer As Scalar"
                #     plt.figure(1)
                #     plt.clf()
                #     plt.plot(np.linspace(0, len(acc_zero_data)/2, len(acc_zero_data)), acc_zero_data)
                #     if mode == "events":
                #         plt.vlines(ICs / 2, 0, 16, colors='r')
                #     plt.title(title)
                #     plt.xlabel("Time / ms")
                #     plt.ylabel(r"Acceleration / $ms^{-2}$")
                #     # plt.show()
                #     if mode == "events":
                #         plt.savefig(events_image_savedir + title)
                #     elif mode == "no_events":
                #         plt.savefig(image_savedir + title)
                #     else:
                #         plt.show()

# all the subfolders in the "/WristShankData/" folder in a list
def wrist_from_aligned_data(subjectStart, subjectEnd, activityTypes=["Walk"]):
    for subjectNum in [x for x in range(subjectStart, subjectEnd) if x not in [20, 22, 46, 47, 48]]:
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum).zfill(2) in goodSubjects:
            subjectDir = "../../AlignedData/TF_{}/".format(str(subjectNum).zfill(2))
            subjectDict = {}
            print(subjectNum)
            for file in os.listdir(subjectDir)[2:3]:
                # load ear data
                trialNum = int(file.split(".")[0].split("-")[-1])
                dataAcc = pd.read_csv(subjectDir+file, usecols=["AccXWrist", "AccYWrist", "AccZWrist"])
                dataGyro = pd.read_csv(subjectDir+file, usecols=["GyroXWrist", "GyroYWrist", "GyroZWrist"])
                dataLear = pd.read_csv(subjectDir+file, usecols=["AccZlear"])
                # get rid of leading zeros
                try:
                    # Acc
                    # plt.plot(dataAcc)
                    # plt.title("{}-{} Acc".format(subjectNum, trialNum))
                    # plt.xlabel("Time / samples")
                    # plt.ylabel("Acceleration / m/s^2")
                    # plt.show()
                    # Gyro
                    plt.plot(filter_wrist(dataGyro["GyroZWrist"].to_numpy(), 36))
                    plt.plot(dataLear - dataLear.mean())
                    accZeroWrist = -dataAcc["AccYWrist"].to_numpy()#calculate_acc_zero(dataAcc.to_numpy())
                    plt.plot(accZeroWrist - np.mean(accZeroWrist))
                    accZeroWrist = filter_wrist(accZeroWrist, 16)
                    plt.plot(accZeroWrist - np.mean(accZeroWrist))
                    plt.title("{}-{} Gyro".format(subjectNum, trialNum))
                    plt.xlabel("Time / samples")
                    plt.ylabel("Acceleration / m/s^2")
                    plt.legend(["Wrist", "Ear", "WristAcc"])
                    plt.show()
                except:
                    print("Unable to plot data for {}-{}".format(subjectNum, trialNum))


def main():
    # process_wrist_multiple(9, 12)
    wrist_from_aligned_data(22, 31)


if __name__ == "__main__":
    main()
