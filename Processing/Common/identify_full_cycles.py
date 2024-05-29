import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json

if __name__ == '__main__':
    # define min/max allowable gait phases for sanity
    minStrideTime = 70
    maxStrideTime = 225
    minStrideDutyCycle = 0.44
    maxStrideDutyCycle = 0.73
    # main file holder
    superArr = np.empty((1, 9))
    superDF = pd.DataFrame(columns=["Subject", "TrialNum", "CycleSide", "CycleNum",
                                    "IC1", "FO1", "IC2", "FO2", "IC3"])
    # loop through raw gait events for all subjects
    for subjectNum in [x for x in range(1, 68) if x not in [11, 16, 46, 47, 48]]:
        # goodSubjects = open("../../Utils/goodTrials",
        #                     "r").read()
        # if str(subjectNum).zfill(2) in goodSubjects:
        subjectDir = "../../C3d/OwnGroundTruth/RawEventsWalksAndTurf/"
        filepath = subjectDir + "TF_{}.json".format(str(subjectNum).zfill(2))
        # read json file
        with open(filepath, 'r') as jsonfile:
            data = json.load(jsonfile)
            for key in data.keys():
                json_str = json.dumps(data[key])
                trialNum = int(key)
                pd_df = pd.read_json(json_str, orient='index').T
                print("{}-{}".format(subjectNum, trialNum))
                gaitCycleDF = pd.DataFrame(columns=["IC1", "FO1", "IC2", "FO2", "IC3"])
                gaitCycleArr = np.empty((1, 9))
                # first, try to extract all the left side cycles
                fullCycleCount = 0
                for i in range(0, len(pd_df.LHC)-1):
                    # find next FO
                    sanityCheckDf = pd_df[pd_df.lt(pd_df.LHC[i+1])].gt(pd_df.LHC[i])
                    if len(sanityCheckDf.RHC[sanityCheckDf.RHC]) == 1\
                        and len(sanityCheckDf.LFO[sanityCheckDf.LFO]) == 1\
                        and len(sanityCheckDf.RFO[sanityCheckDf.RFO]) == 1:
                        # print("Gait cycle is: ", )
                        fullCycleCount += 1
                        RHCVal = pd_df[sanityCheckDf].RHC.dropna().values[0]
                        LFOVal = pd_df[sanityCheckDf].LFO.dropna().values[0]
                        RFOVal = pd_df[sanityCheckDf].RFO.dropna().values[0]
                        gaitCycleArr = np.vstack((gaitCycleArr,
                                                  [subjectNum, trialNum, "Left", fullCycleCount,
                                                   int(pd_df.LHC[i]), int(RFOVal), int(RHCVal), int(LFOVal), int(pd_df.LHC[i+1])]))
                superArr = np.vstack((superArr, gaitCycleArr[1:, :]))
                # then repeat for right hand cycles
                fullCycleCount = 0
                for i in range(0, len(pd_df.RHC) - 1):
                    # find next FO
                    sanityCheckDf = pd_df[pd_df.lt(pd_df.RHC[i + 1])].gt(pd_df.RHC[i])
                    if len(sanityCheckDf.LHC[sanityCheckDf.LHC]) == 1 \
                            and len(sanityCheckDf.RFO[sanityCheckDf.RFO]) == 1 \
                            and len(sanityCheckDf.LFO[sanityCheckDf.LFO]) == 1:
                        # print("Gait cycle is: ", )
                        fullCycleCount += 1
                        LHCVal = pd_df[sanityCheckDf].LHC.dropna().values[0]
                        LFOVal = pd_df[sanityCheckDf].LFO.dropna().values[0]
                        RFOVal = pd_df[sanityCheckDf].RFO.dropna().values[0]
                        gaitCycleArr = np.vstack((gaitCycleArr,
                                                  [subjectNum, trialNum, "Right", fullCycleCount,
                                                   int(pd_df.RHC[i]), int(LFOVal), int(LHCVal),
                                                   int(RFOVal), int(pd_df.RHC[i + 1])]))
                # gaitCycleDF[["Subject", "TrialNum", "CycleSide", "CycleNum",
                #              "IC1", "FO1", "IC2", "FO2", "IC3"]] = gaitCycleArr[1:, :]
                superArr = np.vstack((superArr, gaitCycleArr[1:, :]))
    # save the mega df
    superDF[["Subject", "TrialNum", "CycleSide", "CycleNum",
                             "IC1", "FO1", "IC2", "FO2", "IC3"]] = superArr[1:, :]
    superDF.to_csv("../../C3d/fullCyclesOptical.csv", index=False)



