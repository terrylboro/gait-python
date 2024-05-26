import os
import pandas as pd
import numpy as np

activitiesDF = pd.read_csv('ActivitiesIndex.csv')
cyclesDF = pd.read_csv('fullCyclesOptical.csv')

for subjectNum in [x for x in range(1, 68) if x not in [46, 47, 48]]:
    # print(cyclesDF[cyclesDF["Subject"] == subjectNum])
    # print(activitiesDF[activitiesDF["SubjectNum"] == subjectNum])
    subjectDF = cyclesDF[cyclesDF["Subject"] == subjectNum].copy()
    for column in activitiesDF.columns:
        if column != "SubjectNum":
            trialList = activitiesDF.at[subjectNum-1, column]
            print(subjectNum)
            print(column)
            print(trialList)
            if type(trialList) == np.int64 or type(trialList) == float:
                continue
                # print(subjectDF[subjectDF["TrialNum"] == trialList])
            else:
                trialList = trialList.replace('[', '').replace(']', '')
                trialList = [int(x) for x in trialList.split(",") if x != '[' and x != ']']
                # print(len(cyclesDF[np.logical_and(cyclesDF["TrialNum"].isin(trialList), cyclesDF["Subject"] == subjectNum)]))
                activityIdxList = cyclesDF[np.logical_and(cyclesDF["TrialNum"].isin(trialList), cyclesDF["Subject"] == subjectNum)].index.tolist()
                cyclesDF.loc[activityIdxList, "Activity"] = column
    print(cyclesDF)
    cyclesDF.to_csv('fullCyclesOptical.csv', index=False)
