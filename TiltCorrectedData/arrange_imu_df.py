import pandas as pd
import numpy as np
import os
import csv

# columnNames = open("../Utils/reducedColumnHeaders",
#                              "r").read()[2:]
with open("../Utils/columnHeaders", newline='') as f:
    reader = csv.reader(f)
    columnNames = list(reader)[0][2:]

columnNames.insert(0, "TrialNum")
sides = ["Left", "Right", "Chest", "Pocket"]

for subjectNum in range(26, 68):
    dataPath = "TF_{}".format(str(subjectNum).zfill(2))
    for activity in os.listdir(dataPath):
        print(activity)
        activityDF = pd.DataFrame(columns=columnNames)
        for side in sides:
            dataDir = os.path.join(dataPath, activity, side)
            sideArr = np.empty((0, 10))
            for file in os.listdir(dataDir):
                trialNum = int(file.split("-")[-1].split("_")[0])
                try:
                    data = np.loadtxt(os.path.join(dataDir, file), delimiter=",", skiprows=1)
                    data = np.insert(data, 0, trialNum, axis=1)
                    sideArr = np.vstack((sideArr, data))
                except ValueError:
                    print("No data for {}-{}".format(str(subjectNum).zfill(2), activity))

            sideCols = [x + side for x in ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']]
            # print(sideDF)
            if side == "Left":
                sideCols.insert(0, "TrialNum")
                sideDF = pd.DataFrame(sideArr, columns=sideCols)
                activityDF = sideDF
            else:
                sideDF = pd.DataFrame(sideArr[:, 1:], columns=sideCols)
                activityDF = pd.concat([activityDF, sideDF], axis=1)
        activityDF = activityDF.astype({'TrialNum': 'int32'})
        for k, gr in activityDF.groupby(["TrialNum"]):
            trialNum = gr.iat[0, 0]
            gr["SubjectNum"] = subjectNum
            cols = gr.columns.to_list()
            cols = cols[-1:] + cols[:-1]
            gr = gr[cols]
            gr.to_csv("../IMUSystemData/TF_{}/TF_{}-{}.csv".format(
                str(subjectNum).zfill(2), str(subjectNum).zfill(2), str(trialNum).zfill(2)),
                index=False)



    # print(os.listdir(dataPath))
# for root, dirs, files in os.walk(os.getcwd()):
#     for dir in dirs:
#         if not dir[-1].isdigit():
#             # This is the per activity folder
#             dataPath = os.path.join(root, dir)
#             print(dataPath)
#             # for side in os.listdir(dataPath):
#             #     imuDir = os.path.join(dataPath, side)
#                 # if os.path.isdir(imuDir):
#                 # print(side)