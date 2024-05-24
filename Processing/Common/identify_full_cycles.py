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
    # loop through raw gait events for all subjects
    for subjectNum in [x for x in range(6, 7) if x not in [46, 47, 48]]:
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum).zfill(2) + "," in goodSubjects:
            subjectDir = "../../C3d/OwnGroundTruth/RawEventsWalksAndTurf/"
            for file in os.listdir(subjectDir):
                filepath = subjectDir + file
                # read json file
                with open(filepath, 'r') as jsonfile:
                    data = json.load(jsonfile)
                try:
                    for key in data.keys():
                        json_str = json.dumps(data[key])
                        trialNum = int(key)
                        pd_df = pd.read_json(json_str, orient='index').T
                        print("{}-{}".format(subjectNum, trialNum))
                        # print(pd_df.head())
                        # first, try to extract all the left side cycles
                        for i in range(0, len(pd_df.LHC)):
                            # find next FO
                            sanityCheckDf = pd_df[pd_df.lt(pd_df.LHC[i+1])].gt(pd_df.LHC[i])
                            if len(sanityCheckDf.RHC[sanityCheckDf.RHC]) == 1\
                                and len(sanityCheckDf.LFO[sanityCheckDf.RHC]) == 1\
                                and len(sanityCheckDf.RFO[sanityCheckDf.RHC]) == 1:
                                print("Gait cycle is: ", )
                                print(sanityCheckDf)



                    # json_str = json.dumps(data[str(trialNum).zfill(4)])
                except:
                    # id = str(subjectNum).zfill(2) + str(trialNum).zfill(2)
                    json_str = json.dumps(data[id])



