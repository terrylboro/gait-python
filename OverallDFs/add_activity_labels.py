import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


activityDF = pd.read_csv('../C3d/ActivitiesIndex.csv')

def get_activity_trial_nums(subjectNum):
    # load the activity info
    # activityDF = pd.read_csv('../C3d/ActivitiesIndex.csv')
    subjectDF = activityDF[activityDF["SubjectNum"] == subjectNum]
    walkingTrialNums = [int(x) for x in subjectDF["Walk"].values[0][1:-1].split(",")]
    walkNodTrialNums = [int(x) for x in subjectDF["WalkNod"].values[0][1:-1].split(",")]
    walkShakeTrialNums = [int(x) for x in subjectDF["WalkShake"].values[0][1:-1].split(",")]
    return walkingTrialNums, walkNodTrialNums, walkShakeTrialNums


# plot a walking trial
for subjectNum in [x for x in range(67, 68) if x not in [11, 47, 48, 49]]:
    dataDir = "TF_{}/".format(str(subjectNum).zfill(2))
    walkTrialNums, walkShakeTrialNums, walkNodTrialNums = get_activity_trial_nums(subjectNum)
    # walkTrialNums = get_activity_trial_nums(subjectNum)
    print(dataDir)
    for file in os.listdir(dataDir):
        df = pd.read_csv(os.path.join(dataDir, file))
        trialNum = int(file.split("-")[-1].split(".")[0])
        if trialNum in walkTrialNums:
            # print("{} is a Walk trial".format(file))
            df["Activity"] = "Walk"
        elif trialNum in walkNodTrialNums:
            # print("{} is a WalkNod trial".format(file))
            df["Activity"] = "WalkNod"
        elif trialNum in walkShakeTrialNums:
            # print("{} is a WalkShake trial".format(file))
            df["Activity"] = "WalkShake"
        cols = df.columns.tolist()
        print(cols)
        # print(cols[:2], cols[3:], [cols[2]])
        # cols = cols[:2] + cols[3:] + [cols[2]]
        # cols = cols[:2] + [cols[-1]] + cols[2:-1]
        # # cols = cols[:2] + cols[4:] + [cols[2]]
        # df = df[cols]
        # df.to_csv(os.path.join(dataDir, file), index=False)

