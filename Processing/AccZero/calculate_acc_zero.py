import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, sosfilt, butter


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data


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
                        filtered_data = sosfilt(sos, acc_zero_data.squeeze())
                        # plt.figure()
                        # plt.plot(filtered_data)
                        acc_zero_data = filtered_data + means
                    if mode == "events":
                        if side == "pockets":
                            ICs = find_contacts(acc_zero_data.squeeze(), location="Pocket")
                        else:
                            ICs = find_contacts(acc_zero_data.squeeze())
                        np.savetxt(events_savedir + file, ICs, fmt='%i')
                    if saveData:
                        acc_zero_df = pd.DataFrame({'Time': data["Time"].values, 'Acc0': acc_zero_data.squeeze()})
                        acc_zero_df.to_csv(data_savedir + file, index=False)
                    if saveFig:
                        title = file.split(".")[0] + " " + side + " " + "Accelerometer As Scalar"
                        plt.figure(1)
                        plt.clf()
                        plt.plot(data["Time"].values, acc_zero_data)
                        if mode == "events":
                            plt.vlines(data.loc[ICs, 'Time'], 0, 16, colors='r')
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



def main():
    calculate_acc_zero_multiple(1, 15, activityTypes=["Walk", "WalkShake", "WalkNod", "WalkSlow"], mode="events")
    # calculate_acc_zero_multiple(1, 2, activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
    #                                                    "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"])


if __name__ == "__main__":
    main()

