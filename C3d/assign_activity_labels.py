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
                # if subjectNum in [30, 31, 36, 42, 43, 44, 45, 55, 56, 66, 67]:
                #     cyclesDF.loc[:, "NonTypical"] = 1
                # else:
                #     cyclesDF.loc[:, "NonTypical"] = 0
# print(cyclesDF)
cyclesDF["Condition"] = "Typical"
# print(cyclesDF[cyclesDF["Subject"].isin([30, 31, 36, 42, 43, 44, 45, 55, 56, 66, 67])])
cyclesDF.loc[cyclesDF[cyclesDF["Subject"].isin([30, 31, 36, 42, 43, 44, 45, 55, 56])].index, "Condition"] = "Parkinsons"
cyclesDF.loc[cyclesDF[cyclesDF["Subject"] == 66].index, "Condition"] = "Comorbities"
cyclesDF.loc[cyclesDF[cyclesDF["Subject"] == 67].index, "Condition"] = "Balance"
cyclesDF.drop_duplicates(inplace=True)
cyclesDF.to_csv('fullCyclesOptical.csv', index=False)
