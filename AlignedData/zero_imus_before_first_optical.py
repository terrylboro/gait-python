import os
import pandas as pd
import numpy as np



# import the data
for subjectNum in [x for x in range(61, 62) if x not in [20, 22]]:
    goodSubjects = open("../Utils/goodTrials",
                        "r").read()
    if "," + str(subjectNum).zfill(2) + "," in goodSubjects:
        subjectDir = "TF_{}/".format(str(subjectNum).zfill(2))
        saveDir = "../AlignedZeroedData/" + subjectDir
        subjectDict = {}
        for file in os.listdir(subjectDir):
            trialNum = int(file.split(".")[0].split("-")[-1])
            if trialNum == 3:
                data = pd.read_csv(os.path.join(subjectDir, file))
                print("{}-{}".format(subjectNum, trialNum))
                # find where the first non-zero shank/wrist row is
                firstNonZeroRowIdx = data["AccZShank"].to_numpy().nonzero()[0][0]
                print(data.head(2))
                print("First non-zero: ", firstNonZeroRowIdx)
                data.iloc[:firstNonZeroRowIdx, :] = 0
                print(data.head(2))
                data.to_csv(saveDir+file, index=False)
