import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

# Coordinates of the forceplate (X, Y) only since Z=0
fp1Coords = [(3.2617, -1.0828), (-1.0828, 496.7383), (496.7383, 501.0828), (501.0828, 3.2617)]  # X, Y
fp2Coords = [(69.5797, 502.6288), (62.6288, 1000.4203), (560.4203, 1007.3712), (567.3712, 509.5797)]

# Example of location not working well is in TF_35_0021 where force plate appears
# to register a reading on an initial contact before its y co-ordinate
# Also look at TF_35_11 as the force plate appears to stop registering before the foot leaves
# TF_35_14 - forceplates appear to be in reverse?

gaitEventsDF = pd.read_csv('../C3d/fullCyclesOptical.csv')


def correct_fp_noise(data):
    """ This function finds longest continuous sequence of fp > 0 and return only this data """
    diffs = np.diff(data)
    idx_pairs = np.where(np.diff(np.hstack(([False], diffs == 1, [False]))))[0].reshape(-1, 2)
    return data[idx_pairs[np.diff(idx_pairs, axis=1).argmax(),0] : idx_pairs[np.diff(idx_pairs, axis=1).argmax(),1]+1]


for subjectNum in [x for x in range(1, 68) if x not in [2, 11, 20, 22, 24, 47, 48, 49]]:
    subjectNum2 = str(subjectNum).zfill(2)
    dataDir = "TF_{}/".format(subjectNum2)
    for file in os.listdir(dataDir):
        trialNum = int(file.split('-')[1].split(".")[0])
        # if trialNum == 15:
        # find the corresponding gait cycles
        cyclesDF = gaitEventsDF[np.logical_and(gaitEventsDF.Subject == subjectNum, gaitEventsDF.TrialNum ==  trialNum)]
        print(os.path.join(dataDir, file))
        # print(cyclesDF.IC1)
        df = pd.read_csv(os.path.join(dataDir, file))
        df[["FP1Z", "FP2Z"]] = -df[["FP1Z", "FP2Z"]]
        # Checking data quality #####
        # plt.plot(df[["FP1Z", "FP2Z"]] )
        # plt.show()
        # print(df.FP2Z[df.FP2Z > 0])
        ##############
        # Find the indices of the fp positive signal
        footStrike1Idx = df.FP1Z[df.FP1Z > 0].index.tolist()
        footStrike2Idx = df.FP1Z[df.FP2Z > 0].index.tolist()
        # correct for noise in fp
        try:
            footStrike1Idx = correct_fp_noise(footStrike1Idx)
            footStrike2Idx = correct_fp_noise(footStrike2Idx)
            toleranceVals = [footStrike1Idx[0]-1, footStrike1Idx[0], footStrike1Idx[0]+1, footStrike2Idx[0]-1, footStrike2Idx[0], footStrike2Idx[0]+1]
            # print(toleranceVals)
            # if len(cyclesDF[np.logical_or(cyclesDF.IC1 == footStrike1Idx[0], cyclesDF.IC1 == footStrike2Idx[0])]) == 0:
            if len(cyclesDF[np.logical_or(cyclesDF.IC1.isin(toleranceVals), cyclesDF.IC1.isin(toleranceVals))]) == 0:
                print(footStrike1Idx)
                print(footStrike2Idx)
                print("No Forceplate IC for {}-{}".format(subjectNum2, trialNum))
        except ValueError:
            print("No fp data for {}-{}".format(subjectNum2, trialNum))
        # print(footStrike1Idx)
        # print(footStrike2Idx)
        # if len(cyclesDF[np.logical_or(cyclesDF.IC1 == footStrike1Idx[0], cyclesDF.IC1 == footStrike2Idx[0])]) == 0:
        #     print(footStrike1Idx)
        #     print(footStrike2Idx)
        #     print("No Forceplate IC for {}-{}".format(subjectNum2, trialNum))
        # # extract the corresponding y coordinates of the foot for fp1
        # if df.heelDataLY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828, 501.0828).all()\
        #         and df.toeDataLY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828, 501.0828).all():
        #     print("Complete fp1 strike on Left")
        # elif df.heelDataRY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828, 501.0828).all()\
        #         and df.toeDataRY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828, 501.0828).all():
        #     print("Complete fp1 strike on right")
        # # repeat this for fp2
        # if df.heelDataLY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288, 1000.4203).all()\
        #         and df.toeDataLY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288, 1000.4203).all():
        #     print("Complete fp2 strike on Left")
        # elif df.heelDataRY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288, 1000.4203).all()\
        #         and df.toeDataRY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288, 1000.4203).all():
        #     print("Complete fp2 strike on right")

        # Alternatively, check where foot-on/offs correspond with fp
        # print(cyclesDF.IC1 == footStrike1Idx[0])
        # print(cyclesDF.FO2 == footStrike1Idx[0])
        # print(cyclesDF.IC1 == footStrike2Idx[0])
        # print(cyclesDF.FO2 == footStrike2Idx[0])

        # if len(cyclesDF[np.logical_and(cyclesDF.IC1 == footStrike2Idx[0], cyclesDF.FO2 == footStrike2Idx[-1]+1)]) > 0:
        #     print("Full contact on fp2")
        # if len(cyclesDF[np.logical_and(cyclesDF.IC1 == footStrike1Idx[0], cyclesDF.FO2 == footStrike1Idx[-1]+1)]) > 0:
        #     print("Full contact on fp1")
