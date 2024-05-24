import os
import pandas as pd
import matplotlib.pyplot as plt

# import the data
for subjectNum in [x for x in range(6, 10) if x not in [20, 22]]:
    goodSubjects = open("../Utils/goodTrials",
                        "r").read()
    if "," + str(subjectNum).zfill(2) + "," in goodSubjects:
        subjectDir = "TF_{}/".format(str(subjectNum).zfill(2))
        subjectDict = {}
        for file in os.listdir(subjectDir):
            trialNum = int(file.split(".")[0].split("-")[-1])
            data = pd.read_csv(os.path.join(subjectDir, file))
            plt.plot(data["AccZlear"][data["AccZlear"] > 0])
            plt.title("{}-{}".format(subjectNum, trialNum))
            plt.show()
