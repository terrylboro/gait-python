import os
import pandas as pd

for subjectNum in [65]:#, 66, 67]:
    for trialNum in range(2, 18):
        imuData = pd.read_csv('TF_{}/{}-{}.csv'.format(subjectNum, subjectNum, str(trialNum).zfill(2)))
        imuData = imuData.iloc[:, 1:]
        # print(imuData.head(2))
        overallDF = pd.read_csv('../RealignedOverallDFs/TF_{}/{}-{}.csv'.format(subjectNum, subjectNum, str(trialNum).zfill(2)))
        overallDF.iloc[:, 2:38] = imuData
        print(overallDF.iloc[:, 2:38])
        overallDF.to_csv('../RealignedOverallDFs/TF_{}/{}-{}.csv'.format(subjectNum, subjectNum, str(trialNum).zfill(2)), index=False)