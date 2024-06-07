import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import argrelmax


# Tactic to synchronise the IMUs with the Optical system: #####
# Step 1: Load the overall df, namely columns AccZLeft, AccZRight, FP1Z, FP2Z
# Step 2: Find peaks in the AccZLeft and AccZRight data (should be same)
# Step 3: Identify IC(s) from FP1Z and FP2Z
# Step 4: Figure which if any of these corresponds to a full step using est. stance time
# Step 5: Shift the IMU data by (minus) the difference between IC and peak

saveDir = "../RealignedOverallDFs/"

for subjectNum in [x for x in range(2, 68) if x not in [11, 20, 22, 24, 47, 48, 49]]:
    subjectNum2 = str(subjectNum).zfill(2)
    dataDir = "TF_{}/".format(subjectNum2)
    for file in os.listdir(dataDir):
        print(os.path.join(dataDir, file))
        df = pd.read_csv(os.path.join(dataDir, file))
        df[["FP1Z", "FP2Z"]] = -df[["FP1Z", "FP2Z"]]
        # print(len(df.FP1Z[df.FP2Z > 0]))
        # sns.lineplot(data=df[["FP1Z", "FP2Z"]] / 100)
        # sns.lineplot(data=df["AccZLeft"])
        imuLPeaks = argrelmax(df["AccZLeft"].to_numpy(), order=30)[0]
        # print(imuLPeaks)
        # plt.vlines([imuLPeaks], 0, 10, linestyles="dotted")
        estStrideTime = np.mean(np.diff(imuLPeaks[1:-1]))
        # print("Est Step Time: ", estStrideTime)
        if len(df.FP1Z[df.FP1Z > 0]) > estStrideTime + 5:
            # find the closest peaks
            fpIC = df.FP1Z[df.FP1Z > 0].index[0]  # the first contact on FP
            imuOpticalOffset = np.min(np.abs(imuLPeaks - fpIC))
        elif len(df.FP2Z[df.FP2Z > 0]) > estStrideTime:
            fpIC = df.FP2Z[df.FP2Z > 0].index[0]  # the first contact on FP
            imuOpticalOffset = np.min(np.abs(imuLPeaks - fpIC))
        else:
            print("Not clean contact on FP for {}".format(file))
            imuOpticalOffset = 0
        print("Offset: ", imuOpticalOffset)
        df[["AccZLeft", "AccZRight"]] = df[["AccZLeft", "AccZRight"]].shift(-imuOpticalOffset)
        df.to_csv(os.path.join(saveDir, "TF_{}".format(subjectNum2), file), index=False)
        # sns.lin)eplot(data=df[["FP1Z", "FP2Z"]] / 100)
        #         # sns.lineplot(data=df["AccZLeft"])
        #         # # plt.vlines(fpIC, 0, 20, linestyles="dashed")
        #         # plt.title(file)
        #         # plt.show(
