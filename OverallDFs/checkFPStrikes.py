import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

# Coordinates of the forceplate (X, Y) only since Z=0
fp1Coords = [(3.2617, -1.0828), (-1.0828, 496.7383), (496.7383, 501.0828), (501.0828, 3.2617)]  # X, Y
fp2Coords = [(69.5797, 502.6288), (62.6288, 1000.4203), (560.4203, 1007.3712), (567.3712, 509.5797)]
heelOffsetVal = 20  # to correct for distance between heel and heel marker
toeOffsetVal = 30  # to correct for distance between toe and toe marker

# Example of location not working well is in TF_35_0021 where force plate appears
# to register a reading on an initial contact before its y co-ordinate
# Also look at TF_35_11 as the force plate appears to stop registering before the foot leaves
# TF_35_14 - forceplates appear to be in reverse?

gaitEventsDF = pd.read_csv('../C3d/fullCyclesOptical.csv')
gaitEventsDF["IsFullFPStrike"] = False


def correct_fp_noise(data):
    """ This function finds longest continuous sequence of fp > 0 and return only this data """
    diffs = np.diff(data)
    idx_pairs = np.where(np.diff(np.hstack(([False], diffs == 1, [False]))))[0].reshape(-1, 2)
    if idx_pairs.size:
        return data[idx_pairs[np.diff(idx_pairs, axis=1).argmax(),0] : idx_pairs[np.diff(idx_pairs, axis=1).argmax(),1]+1]


def match_fp_with_cycles(subjectNum2, trialNum, footStrike1Idx, footStrike2Idx):
    # check if gait events roughly line up
    try:
        footStrike1Idx = correct_fp_noise(footStrike1Idx)
        toleranceVals = [footStrike1Idx[0] - 1, footStrike1Idx[0], footStrike1Idx[0] + 1, footStrike2Idx[0] - 1,
                         footStrike2Idx[0], footStrike2Idx[0] + 1]
        # print(toleranceVals)
        # if len(cyclesDF[np.logical_or(cyclesDF.IC1 == footStrike1Idx[0], cyclesDF.IC1 == footStrike2Idx[0])]) == 0:
        if len(cyclesDF[np.logical_or(cyclesDF.IC1.isin(toleranceVals), cyclesDF.IC1.isin(toleranceVals))]) == 0:
            print(footStrike1Idx)
            print(footStrike2Idx)
            print("No Forceplate IC for {}-{}".format(subjectNum2, trialNum))
    except ValueError:
        print("No fp data for {}-{}".format(subjectNum2, trialNum))


for subjectNum in [x for x in range(1, 68) if x not in [11, 47, 48, 49]]:
    subjectNum2 = str(subjectNum).zfill(2)
    dataDir = "TF_{}/".format(subjectNum2)
    for file in os.listdir(dataDir):
        trialNum = int(file.split('-')[1].split(".")[0])
        # if trialNum == 2:
        # find the corresponding gait cycles
        cyclesDF = gaitEventsDF[np.logical_and(gaitEventsDF.Subject == subjectNum, gaitEventsDF.TrialNum == trialNum)]
        print(os.path.join(dataDir, file))
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
        # correct for spurious noise by finding longest sequence
        footStrike1Idx = correct_fp_noise(footStrike1Idx)
        footStrike2Idx = correct_fp_noise(footStrike2Idx)

        # extract the corresponding y coordinates of the foot for fp1
        # first ensuring that there is a strike at all
        validFSRange = 5
        icDiffs = []
        foDiffs = []
        # print(gaitEventsDF.loc[np.logical_and(gaitEventsDF.Subject == subjectNum, gaitEventsDF.TrialNum == trialNum), "FO2"])
        if footStrike1Idx:
            if df.heelDataLY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828 - heelOffsetVal,
                                                                               501.0828 - heelOffsetVal).all() \
                    and df.toeDataLY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828 - toeOffsetVal,
                                                                                       501.0828 - toeOffsetVal).all():
                # mark that this cycle is a full strike on the fp
                try:
                    cycleIdx = cyclesDF[cyclesDF.IC1.between(footStrike1Idx[0] - validFSRange, footStrike1Idx[0] + validFSRange)].index.to_list()[0]
                    gaitEventsDF.loc[cycleIdx, "IsFullFPStrike"] = True
                    # find the difference between our IC and the fp IC, then correct using this difference
                    icDiff = int(gaitEventsDF.at[cycleIdx, "IC1"]) - int(footStrike1Idx[0])
                    gaitEventsDF.loc[cycleIdx, "IC1"] -= icDiff
                    foDiff = gaitEventsDF.loc[cycleIdx, "FO2"] - (footStrike1Idx[-1] + 1)
                    gaitEventsDF.loc[cycleIdx, "FO2"] -= foDiff
                    icDiffs.append(icDiff)
                    foDiffs.append(foDiff)
                except IndexError:
                    print("Footstrike not clean - fp noisy or prev. foot activated fp early")
            elif df.heelDataRY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828 - heelOffsetVal,
                                                                                 501.0828 - heelOffsetVal).all() \
                    and df.toeDataRY.loc[footStrike1Idx[0]:footStrike1Idx[-1]].between(-1.0828 - toeOffsetVal,
                                                                                       501.0828 - toeOffsetVal).all():
                # mark that this cycle is a full strike on the fp
                try:
                    cycleIdx = cyclesDF[cyclesDF.IC1.between(footStrike1Idx[0] - validFSRange, footStrike1Idx[0] + validFSRange)].index.to_list()[0]
                    gaitEventsDF.loc[cycleIdx, "IsFullFPStrike"] = True
                    # find the difference between our IC and the fp IC, then correct using this difference
                    icDiff = int(gaitEventsDF.at[cycleIdx, "IC1"]) - int(footStrike1Idx[0])
                    gaitEventsDF.loc[cycleIdx, "IC1"] -= icDiff
                    foDiff = gaitEventsDF.loc[cycleIdx, "FO2"] - (footStrike1Idx[-1] + 1)
                    gaitEventsDF.loc[cycleIdx, "FO2"] -= foDiff
                    icDiffs.append(icDiff)
                    foDiffs.append(foDiff)
                except IndexError:
                    print("Footstrike not clean - fp noisy or prev. foot activated fp early")
        # repeat this for fp2
        if footStrike2Idx:
            if df.heelDataLY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288 - heelOffsetVal,
                                                                               1000.4203 - heelOffsetVal).all() \
                    and df.toeDataLY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288 - toeOffsetVal,
                                                                                       1000.4203 - toeOffsetVal).all():
                # mark that this cycle is a full strike on the fp
                try:
                    cycleIdx = cyclesDF[cyclesDF.IC1.between(footStrike2Idx[0] - validFSRange, footStrike2Idx[0] + validFSRange)].index.to_list()[0]
                    gaitEventsDF.loc[cycleIdx, "IsFullFPStrike"] = True
                    # find the difference between our IC and the fp IC, then correct using this difference
                    icDiff = int(gaitEventsDF.at[cycleIdx, "IC1"]) - int(footStrike2Idx[0])
                    gaitEventsDF.loc[cycleIdx, "IC1"] -= icDiff
                    foDiff = gaitEventsDF.loc[cycleIdx, "FO2"] - (footStrike2Idx[-1] + 1)
                    gaitEventsDF.loc[cycleIdx, "FO2"] -= foDiff
                    icDiffs.append(icDiff)
                    foDiffs.append(foDiff)
                except IndexError:
                    print("Footstrike not clean - fp noisy or prev. foot activated fp early")
            elif df.heelDataRY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288 - heelOffsetVal,
                                                                                 1000.4203 - heelOffsetVal).all() \
                    and df.toeDataRY.loc[footStrike2Idx[0]:footStrike2Idx[-1]].between(502.6288 - toeOffsetVal,
                                                                                       1000.4203 - toeOffsetVal).all():
                # mark that this cycle is a full strike on the fp
                try:
                    cycleIdx = cyclesDF[cyclesDF.IC1.between(footStrike2Idx[0] - validFSRange, footStrike2Idx[0] + validFSRange)].index.to_list()[0]
                    gaitEventsDF.loc[cycleIdx, "IsFullFPStrike"] = True
                    # find the difference between our IC and the fp IC, then correct using this difference
                    icDiff = int(gaitEventsDF.at[cycleIdx, "IC1"]) - int(footStrike2Idx[0])
                    gaitEventsDF.loc[cycleIdx, "IC1"] -= icDiff
                    foDiff = gaitEventsDF.loc[cycleIdx, "FO2"] - (footStrike2Idx[-1] + 1)
                    gaitEventsDF.loc[cycleIdx, "FO2"] -= foDiff
                    # icDiffs.append(icDiff)
                    # foDiffs.append(foDiff)
                except IndexError:
                    print("Footstrike not clean - fp noisy or prev. foot activated fp early")



# log this information to the corresponding df
gaitEventsDF.to_csv("gaitCycleDetails.csv", index=False)


