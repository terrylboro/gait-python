import os
import pandas as pd

activitiesDF = pd.DataFrame(columns=["SubjectNum", "Walk", "WalkNod", "WalkShake", "WalkSlow",
                                     "Sit2Stand", "Stand2Sit", "TUG", "PickUp", "Reach", "Static",
                                     "ShoeBox", "Floor2Turf", "Turf2Floor"],
                            dtype=object)

for dir in os.listdir(os.getcwd()):
    if not dir.endswith('.py'):
        subjectNum = int(dir.split('_')[1])
        activitiesDF.at[subjectNum, "SubjectNum"] = subjectNum
        # walkTrials = []
        # walkNodTrials = []
        # walkShakeTrials = []
        # walkSlowTrials = []
        # sit2StandTrials = []
        # stand2SitTrials = []
        # tugTrials = []
        # reachTrials = []
        # staticTrials = []
        # shoeBoxTrials = []
        # floor2TurfTrials = []
        # turf2FloorTrials = []
        for activity in os.listdir(os.path.join(os.getcwd(), dir)):
            activityDir = os.path.join(os.getcwd(), dir, activity, "Chest")
            activityList = []
            for file in os.listdir(activityDir):
                trialNum = int(file.split("-")[1].split("_")[0])
                activityList.append(trialNum)
            print("Activity: ", activity)
            print("Trials: ", activityList)
            # activitiesDF[activity].append(activityList)
            activitiesDF.at[subjectNum, activity] = activityList

activitiesDF.to_csv("ActivitiesIndex.csv", index=False)


