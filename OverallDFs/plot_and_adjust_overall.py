import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


activityDF = pd.read_csv('../C3d/ActivitiesIndex.csv')


# plot a walking trial
for subjectNum in [x for x in range(60, 68) if x not in [11, 20, 22, 24, 47, 48, 49]]:
    dataDir = "TF_{}/".format(str(subjectNum).zfill(2))
    print(dataDir)
    for file in os.listdir(dataDir):
        df = pd.read_csv(os.path.join(dataDir, file))
        trialNum = int(file.split("-")[-1].split(".")[0])
        if trialNum == 4:
            sns.lineplot(data=df[["AccZLeft", "AccYWrist"]])
            wristResAcc = np.sqrt(np.sum(np.square(df[["AccXWrist", "AccYWrist", "AccZWrist"]]), axis=1))
            # print(wristResAcc[wristResAcc != 0])
            sns.lineplot(data=wristResAcc)
            # sns.lineplot(data=df["AccYWrist"])
            fp1NonZero = df["FP1Z"][df["FP1Z"] < 0]
            fp1NonZero = fp1NonZero[fp1NonZero.notna()].abs()
            fp2NonZero = df["FP2Z"][df["FP2Z"] < 0]
            fp2NonZero = fp2NonZero[fp2NonZero.notna()].abs()
            fp1NonZeroNormalised = fp1NonZero.div(fp1NonZero.max()) * 10
            fp2NonZeroNormalised = fp2NonZero.div(fp2NonZero.max()) * 10
            # print(fpNonZeroNormalised)
            # print(df["FP1Z"].div(max(df["FP1Z"].to_numpy()), fill_value=0).mul(10, fill_value=0))
            sns.lineplot(data=fp1NonZeroNormalised)
            sns.lineplot(data=fp2NonZeroNormalised)
            plt.vlines([fp1NonZeroNormalised.index[0], fp2NonZeroNormalised.index[0]], 0, 10, linestyles='solid', colors='r')
            plt.title("{}-{}".format(subjectNum, trialNum))
            plt.show()
