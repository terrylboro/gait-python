import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data


def prep_folders(subject, activityTypes):
    if not os.path.exists(subject): os.mkdir(subject)
    for activity in activityTypes:
        if not os.path.exists(subject + "/" + activity): os.mkdir(subject + "/" + activity)
        if not os.path.exists(subject + "/" + activity + "/Right/"): os.mkdir(subject + "/" + activity + "/Right/")
        if not os.path.exists(subject + "/" + activity + "/Left/"): os.mkdir(subject + "/" + activity + "/Left/")
        if not os.path.exists(subject + "/" + activity + "/Chest/"): os.mkdir(subject + "/" + activity + "/Chest/")
        if not os.path.exists(subject + "/" + activity + "/Pocket/"): os.mkdir(subject + "/" + activity + "/Pocket/")


def calculate_acc_zero_multiple(subjectStart, subjectEnd, activityTypes=["Walk"]):
    # all the subfolders in the "/FilteredData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        prep_folders(subject, activityTypes)
        for side in ["Left", "Right", "Chest", "Pocket"]:
            for activity in activityTypes:
                loaddir = "../../NEDData/" + subject + "/" + activity + "/" + side + "/"
                savedir = subject + "/" + activity + "/" + side + "/"
                for file in os.listdir(loaddir):
                    filepath = loaddir + file
                    data = pd.read_csv(filepath, usecols=["Time", "AccX", "AccY", "AccZ"])
                    # print(data[["AccX", "AccY", "AccZ"]])
                    acc_zero_data = calculate_acc_zero(data[["AccX", "AccY", "AccZ"]].values)
                    title = file.split(".")[0] + " " + side + " " + "As Scalar"
                    plt.figure(1)
                    plt.clf()
                    plt.plot(data["Time"].values, acc_zero_data)
                    plt.title(title)
                    plt.xlabel("Time / ms")
                    plt.ylabel(r"Acceleration / $ms^{-2}$")
                    plt.savefig(savedir + title)


def main():
    calculate_acc_zero_multiple(1, 15, activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
                                                       "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"])


if __name__ == "__main__":
    main()

