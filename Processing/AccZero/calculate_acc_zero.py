import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, sosfilt, butter


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
                                mode="no_events"):
    # all the subfolders in the "/FilteredData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
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
                    # print(data[["AccX", "AccY", "AccZ"]])
                    acc_zero_data = calculate_acc_zero(data[["AccX", "AccY", "AccZ"]].values)
                    if side == "Pocket":
                        means = np.mean(acc_zero_data)
                        acc_zero_data = acc_zero_data - means
                        sos = butter(2, 1.5, btype="low", fs=100, output='sos')
                        filtered_data = sosfilt(sos, acc_zero_data)
                        # plt.figure()
                        # plt.plot(filtered_data)
                        acc_zero_data = filtered_data + means
                    if mode == "events":
                        if side == "pockets":
                            ICs = find_contacts(acc_zero_data, location="Pocket")
                        else:
                            ICs = find_contacts(acc_zero_data)
                        # np.savetxt(events_savedir + file, ICs, fmt='%i')
                        np.savetxt(events_savedir + file, data.loc[ICs, 'Time'], fmt='%i')
                    if saveData:
                        acc_zero_df = pd.DataFrame({'Time': data["Time"].values, 'Acc0': acc_zero_data})
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
                    # print(data[["AccX", "AccY", "AccZ"]])
                    acc_zero_data = calculate_acc_zero(data)
                    # if side == "Wrist":
                    #     means = np.mean(acc_zero_data)
                    #     acc_zero_data = acc_zero_data - means
                    #     sos = butter(2, 1.5, btype="low", fs=100, output='sos')
                    #     filtered_data = sosfilt(sos, acc_zero_data.squeeze())
                    #     # plt.figure()
                    #     # plt.plot(filtered_data)
                    #     acc_zero_data = filtered_data + means
                    if mode == "events":
                        ICs = find_contacts(acc_zero_data, location=side)
                        # np.savetxt(events_savedir + file, ICs, fmt='%i')
                        np.savetxt(events_savedir + file, ICs / 2, fmt='%i')
                    if saveData:
                        acc_zero_df = pd.DataFrame({'Time': np.linspace(0, len(acc_zero_data)/2, len(acc_zero_data)), 'Acc0': acc_zero_data})
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


def compare_two_trials():
    chest_data = pd.read_csv("Data/TF_01/WalkSlow/Chest/TF_01-22_NED.csv")
    # ear_data = pd.read_csv("Data/TF_01/WalkSlow/Left/TF_01-22_NED.csv")
    # pocket_data = pd.read_csv("Data/TF_01/WalkSlow/Pocket/TF_01-22_NED.csv")
    shank_data = pd.read_csv("Data/TF_01/Walk/Shank/TF_01-21shank.csv")
    # wrist_data = pd.read_csv("Data/TF_01/Walk/Wrist/TF_01-21wrist.csv")
    plt.figure(1)
    plt.clf()
    plt.plot((shank_data["Time"].values + 890) / 1000, shank_data["Acc0"].values)
    # plt.plot((wrist_data["Time"].values + 880) / 1000, wrist_data["Acc0"].values)
    plt.plot(chest_data["Time"].values / 1000, chest_data["Acc0"].values)
    # plt.plot(ear_data["Time"].values / 1000, ear_data["Acc0"].values)
    # plt.plot(pocket_data["Time"].values / 1000, pocket_data["Acc0"].values)
    plt.title("Shank vs Chest")
    plt.xlabel("Time / s")
    plt.ylabel(r"Acceleration / $ms^{-2}$")
    # plt.legend(["Shank", "Wrist", "Chest", "Ear", "Pocket"])
    plt.legend(["Shank", "Chest"])
    plt.show()


def main():
    compare_two_trials()
    # calculate_acc_zero_delsys(1, 2, activityTypes=["Walk"], mode="events")
    # calculate_acc_zero_multiple(1, 15, activityTypes=["TUG"], mode="events")
    # calculate_acc_zero_multiple(1, 2, activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
    #                                                    "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"])


if __name__ == "__main__":
    main()

