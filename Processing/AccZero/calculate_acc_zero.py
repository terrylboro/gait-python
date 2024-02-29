import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, sosfilt, filtfilt, butter


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def prep_folders(subject, activityTypes):
    for activity in activityTypes:
        for category in ["Contact Events/", "Data/", "Graphs/", "Contact Event Graphs/"]:
            if not os.path.exists("Graphs"): os.mkdir("Graphs")
            if not os.path.exists("Data"): os.mkdir("Data")
            if not os.path.exists(category + subject + "/"):
                os.mkdir(category + subject + "/")
            if not os.path.exists(category + subject + "/" + activity):
                os.mkdir(category + subject + "/" + activity)
            if not os.path.exists(category + subject + "/" + activity + "/Right/"):
                os.mkdir(category + subject + "/" + activity + "/Right/")
            if not os.path.exists(category + subject + "/" + activity + "/Left/"):
                os.mkdir(category + subject + "/" + activity + "/Left/")
            if not os.path.exists(category + subject + "/" + activity + "/Chest/"):
                os.mkdir(category + subject + "/" + activity + "/Chest/")
            if not os.path.exists(category + subject + "/" + activity + "/Pocket/"):
                os.mkdir(category + subject + "/" + activity + "/Pocket/")


def find_contacts(data, location=None):
    if location == "Pocket":
        peaks, _ = find_peaks(data, prominence=0.25, distance=45)
    elif location == "Shank":
        peaks, _ = find_peaks(data, prominence=20, distance=450)
    elif location == "Wrist":
        peaks, _ = find_peaks(data, prominence=1, distance=450)
    else:
        peaks, _ = find_peaks(data, prominence=1, height=12, distance=45)
    return peaks.astype(int)


def calculate_acc_zero_multiple(subjectStart, subjectEnd, activityTypes=["Walk"], saveData=True, saveFig=True,
                                mode="no_events", isTF=True):
    # all the subfolders in the "/FilteredData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        if isTF:
            subject = "TF_" + str(subject_num).zfill(2)
        else:
            subject = "NTF_" + str(subject_num).zfill(2)
        prep_folders(subject, activityTypes)
        for side in ["Left", "Right", "Chest", "Pocket"]:
            for activity in activityTypes:
                loaddir = "../../NEDData/" + subject + "/" + activity + "/" + side + "/"
                image_savedir = "Graphs/" + subject + "/" + activity + "/" + side + "/"
                data_savedir = "Data/" + subject + "/" + activity + "/" + side + "/"
                events_savedir = "Contact Events/" + subject + "/" + activity + "/" + side + "/"
                events_image_savedir = "Contact Event Graphs/" + subject + "/" + activity + "/" + side + "/"
                for file in os.listdir(loaddir):
                    filepath = loaddir + file
                    data = pd.read_csv(filepath, usecols=["Time", "AccX", "AccY", "AccZ"])
                    gyro_data = pd.read_csv(filepath, usecols=["Time", "GyroX", "GyroY", "GyroZ"])
                    # print(data[["AccX", "AccY", "AccZ"]])
                    acc_zero_data = calculate_acc_zero(data[["AccX", "AccY", "AccZ"]].values)
                    gyro_zero_data = calculate_acc_zero(gyro_data[["GyroX", "GyroY", "GyroZ"]].values)
                    if side == "Chest":
                        b, a = butter(2, 25, btype="low", fs=100, output='ba')
                        acc_zero_data = filtfilt(b, a, acc_zero_data)
                    if side == "Pocket":
                        b, a = butter(2, 15, btype="low", fs=100, output='ba')
                        acc_zero_data = filtfilt(b, a, acc_zero_data)
                    if mode == "events":
                        if side == "pockets":
                            ICs = find_contacts(acc_zero_data, location="Pocket")
                        else:
                            ICs = find_contacts(acc_zero_data)
                        # np.savetxt(events_savedir + file, ICs, fmt='%i')
                        np.savetxt(events_savedir + file, data.loc[ICs, 'Time'], fmt='%i')
                    if saveData:
                        acc_zero_df = pd.DataFrame({'Time': data["Time"].values, 'Acc0': acc_zero_data, 'Gyro0': gyro_zero_data})
                        acc_zero_df.to_csv(data_savedir + file, index=False)
                    if saveFig:
                        title = file.split(".")[0] + " " + side + " " + "Accelerometer As Scalar"
                        plt.figure(1)
                        plt.clf()
                        plt.plot(data["Time"].values / 10, acc_zero_data)
                        if mode == "events":
                            plt.vlines(data.loc[ICs, 'Time'] / 10, 0, 16, colors='r')
                        plt.title(title)
                        plt.xlabel("Time / ms")
                        plt.ylabel(r"Acceleration / $ms^{-2}$")
                        # plt.show()
                        if mode == "events":
                            plt.savefig(events_image_savedir + title)
                        elif mode == "no_events":
                            plt.savefig(image_savedir + title)
                        else:
                            plt.show()


def calculate_acc_zero_delsys(subjectStart, subjectEnd, activityTypes=["Walk"], saveData=True, saveFig=True,
                                mode="no_events"):
    # all the subfolders in the "/WristShankData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        for side in ["Shank", "Wrist"]:
            for activity in activityTypes:
                # ensure folders are there to store the outputs
                for category in ["Contact Events/", "Data/", "Graphs/", "Contact Event Graphs/"]:
                    if not os.path.exists(category + subject + "/" + activity + "/"):
                        os.mkdir(category + subject + "/" + activity + "/")
                    if not os.path.exists(category + subject + "/" + activity + "/" + side):
                        os.mkdir(category + subject + "/" + activity + "/" + side)
                loaddir = "../../WristShankData/" + subject + "/" + activity + "/" + side + "/"
                image_savedir = "Graphs/" + subject + "/" + activity + "/" + side + "/"
                data_savedir = "Data/" + subject + "/" + activity + "/" + side + "/"
                events_savedir = "Contact Events/" + subject + "/" + activity + "/" + side + "/"
                events_image_savedir = "Contact Event Graphs/" + subject + "/" + activity + "/" + side + "/"
                for file in os.listdir(loaddir):
                    filepath = loaddir + file
                    data = np.loadtxt(filepath, usecols=range(0, 3), delimiter=",")
                    gyro_data = np.loadtxt(filepath, usecols=range(3, 6), delimiter=",")
                    # print(data[["AccX", "AccY", "AccZ"]])
                    acc_zero_data = calculate_acc_zero(data)
                    gyro_zero_data = calculate_acc_zero(gyro_data)
                    if side == "Shank":
                        b, a = butter(2, 100, btype="low", fs=1000, output='ba')
                        filtered_data = filtfilt(b, a, acc_zero_data)
                        acc_zero_data = filtered_data
                    elif side == "Wrist":
                        b, a = butter(2, 100, btype="low", fs=1000, output='ba')
                        filtered_data = filtfilt(b, a, acc_zero_data)
                        acc_zero_data = filtered_data
                    # plt.figure()
                    # plt.plot(filtered_data)
                    # acc_zero_data = filtered_data + means
                    if mode == "events":
                        ICs = find_contacts(acc_zero_data, location=side)
                        # np.savetxt(events_savedir + file, ICs, fmt='%i')
                        np.savetxt(events_savedir + file, ICs / 2, fmt='%i')
                    if saveData:
                        acc_zero_df = pd.DataFrame({'Time': np.linspace(0, len(acc_zero_data)/2, len(acc_zero_data)),
                                                    'Acc0': acc_zero_data, 'Gyro0': gyro_zero_data})
                        acc_zero_df.to_csv(data_savedir + file, index=False)
                    if saveFig:
                        title = file.split(".")[0] + " " + side + " " + "Accelerometer As Scalar"
                        plt.figure(1)
                        plt.clf()
                        plt.plot(np.linspace(0, len(acc_zero_data)/2, len(acc_zero_data)), acc_zero_data)
                        if mode == "events":
                            plt.vlines(ICs / 2, 0, 16, colors='r')
                        plt.title(title)
                        plt.xlabel("Time / ms")
                        plt.ylabel(r"Acceleration / $ms^{-2}$")
                        # plt.show()
                        if mode == "events":
                            plt.savefig(events_image_savedir + title)
                        elif mode == "no_events":
                            plt.savefig(image_savedir + title)
                        else:
                            plt.show()


def compare_two_trials(subject):
    delsys_offset = 0#20#86
    subject = str(subject).zfill(2)
    activity = "Walk"
    for trial in range(3, 13):
        chest_data = pd.read_csv("Data/TF_"+subject+"/"+activity+"/Chest/TF_"+subject+"-"+str(trial).zfill(2)+"_NED.csv")
        ear_data = pd.read_csv("Data/TF_"+subject+"/"+activity+"/Right/TF_"+subject+"-"+str(trial).zfill(2)+"_NED.csv")
        pocket_data = pd.read_csv("Data/TF_"+subject+"/"+activity+"/Pocket/TF_"+subject+"-"+str(trial).zfill(2)+"_NED.csv")
        shank_data = pd.read_csv("Data/TF_"+subject+"/"+activity+"/Shank/TF_"+subject+"-"+str(trial).zfill(2)+"shank.csv")
        wrist_data = pd.read_csv("Data/TF_"+subject+"/"+activity+"/Wrist/TF_"+subject+"-"+str(trial).zfill(2)+"wrist.csv")
        plt.figure(1)
        plt.clf()
        plt.plot((shank_data["Time"].values + delsys_offset) / 1000, shank_data["Acc0"].values)
        plt.plot(wrist_data["Time"].values / 1000, wrist_data["Acc0"].values)
        # plt.plot((chest_data["Time"].values % 65536) / 1000, chest_data["Acc0"].values)
        plt.plot((chest_data["Time"].values % 65536) / 1000, ear_data["Acc0"].values)
        # plt.plot((chest_data["Time"].values % 65536) / 1000, pocket_data["Acc0"].values)

        # plt.plot((shank_data["Time"].values + delsys_offset) / 1000, shank_data["Gyro0"].values)
        # # plt.plot(wrist_data["Time"].values / 1000, wrist_data["Gyro0"].values)
        # plt.plot(chest_data["Time"].values / 1000, chest_data["Gyro0"].values)
        # plt.plot(ear_data["Time"].values / 1000, ear_data["Gyro0"].values)
        # # plt.plot(pocket_data["Time"].values / 1000, pocket_data["Gyro0"].values)

        plt.title("Comparison of Resultant Accelerometer Signals by Location for Participant " + subject + " Trial " + str(trial))
        plt.xlabel("Time / s")
        plt.ylabel(r"Acceleration / $ms^{-2}$")
        # plt.legend(["Shank", "Wrist", "Chest", "Ear", "Pocket"])
        plt.legend(["Shank", "Wrist", "Ear"])
        # plt.legend(["Chest", "Ear"])#, "Pocket"])
        # plt.legend(["Ear"])
        plt.show()


def main():
    # for subject in range(9, 13):
    #     compare_two_trials(subject)
    # compare_two_trials()
    # calculate_acc_zero_delsys(9, 13, activityTypes=["Walk"])#["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
    #                                                    # "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"], mode="no_events")
    # calculate_acc_zero_multiple(17, 20, activityTypes=["Walk"], mode="no_events")
    calculate_acc_zero_multiple(30, 32, activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
                                                       "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"], isTF=False)


if __name__ == "__main__":
    main()

