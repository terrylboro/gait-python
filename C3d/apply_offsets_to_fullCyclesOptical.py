import os
import pandas as pd
import numpy as np

offsetDF = pd.read_csv('offsets.csv')
gaitEventsDF = pd.read_csv('fullCyclesOptical.csv')
# gaitEventsDF = gaitEventsDF[gaitEventsDF.Subject > 64]

# print(offsetDF)
# print(gaitEventsDF)

for i in range(0, len(offsetDF)):
    subjectNum = offsetDF.iloc[i, 0]
    trialNum = offsetDF.iloc[i, 1]
    offset = offsetDF.iloc[i, 2]
    print(subjectNum, trialNum, offset)
    indicesToAlter = gaitEventsDF[np.logical_and(gaitEventsDF.Subject == subjectNum, gaitEventsDF.TrialNum == trialNum)].index
    print(gaitEventsDF.iloc[indicesToAlter, 4:9])
    gaitEventsDF.iloc[indicesToAlter, 4:9] += offset
    print(gaitEventsDF.iloc[indicesToAlter, 4:9])

gaitEventsDF.to_csv('fullCyclesOptical.csv', index=False)
