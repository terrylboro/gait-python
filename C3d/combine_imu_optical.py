import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

imuDataDir = "../AlignedZeroedData/"
opticalDataDir = ""

if __name__ == '__main__':
    for subjectNum in [61]:#[x for x in range(58, 68) if x not in [40, 41, 46, 47, 48, 61]]:
        # loop through the csv for each trial
        filepath = os.path.join(imuDataDir, "TF_{}".format(subjectNum))
        for imuFile in os.listdir(filepath):
            trialNum = int(imuFile.split('-')[-1].split(".")[0])
            print("{}-{}".format(subjectNum, trialNum))
            # if int(trialNum) in [2, 3, 4]:
            imuDF = pd.read_csv(os.path.join(filepath, imuFile))
            opticalDF = pd.read_csv("{}-{}-opticalDF.csv".format(subjectNum, str(trialNum).zfill(2)))
            combinedDF = pd.concat([imuDF, opticalDF], axis=1)
            combinedDF.to_csv("{}-{}-combinedDF.csv".format(subjectNum, str(trialNum).zfill(2)), index=False)
