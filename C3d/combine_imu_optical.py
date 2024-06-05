import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from calculate_joint_angles import get_walking_trial_nums

imuDataDir = "../IMUSystemData/"#"../AlignedZeroedData/"
opticalDataDir = "../OpticalDFs/"


def combine_alignZero_and_optical(imuDataDir, opticalDataDir):
    for subjectNum in [x for x in range(1, 68) if x not in [11, 46, 47, 48]]:
        # loop through the csv for each trial
        filepath = os.path.join(opticalDataDir, "TF_{}".format(str(subjectNum).zfill(2)))
        for file in os.listdir(filepath):
            trialNum = int(file.split('-')[-1].split(".")[0])
            print("{}-{}".format(subjectNum, trialNum))
            opticalDF = pd.read_csv(os.path.join(filepath,file))
            imuDF = pd.read_csv(os.path.join(imuDataDir, "TF_{}".format(str(subjectNum).zfill(2)), "TF_"+file))
            overallDF = pd.concat([imuDF, opticalDF], axis=1)
            overallDF['SubjectNum'] = subjectNum
            overallDF["TrialNum"] = trialNum
            overallDF[["SubjectNum", "TrialNum"]] = overallDF[["SubjectNum", "TrialNum"]].astype("int32")
            overallDF.to_csv("../OverallDFs/TF_{}/{}-{}.csv".format(
                str(subjectNum).zfill(2), str(subjectNum).zfill(2), str(trialNum).zfill(2)), index=False)
            # # if int(trialNum) in [2, 3, 4]:
            # imuDF = pd.read_csv(os.path.join(filepath, imuFile))
            # opticalDF = pd.read_csv("{}-{}-opticalDF.csv".format(subjectNum, str(trialNum).zfill(2)))
            # combinedDF = pd.concat([imuDF, opticalDF], axis=1)
            # # if all values in first row are
            # if combinedDF.eq(0, axis=0).all(1):
            #     combinedDF = combinedDF.iloc[1:, :]
            # combinedDF.to_csv("{}-{}-combinedDF.csv".format(subjectNum, str(trialNum).zfill(2)), index=False)


def produce_combined_data_from_scratch(imuDataDir, opticalDataDir):
    for subjectNum in [60]:
        imuData = pd.read_csv(os.path.join(imuDataDir, "TF_{}".format(str(subjectNum).zfill(2))))



if __name__ == '__main__':
    combine_alignZero_and_optical(imuDataDir, opticalDataDir)
