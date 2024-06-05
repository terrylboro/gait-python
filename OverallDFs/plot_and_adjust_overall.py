import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


activityDF = pd.read_csv('../C3d/ActivitiesIndex.csv')


# plot a walking trial
for subjectNum in [x for x in range(66, 67) if x not in [11, 47, 48, 49]]:
    dataDir = "TF_{}/".format(str(subjectNum).zfill(2))
    print(dataDir)
    for file in os.listdir(dataDir):
        df = pd.read_csv(os.path.join(dataDir, file))
        trialNum = int(file.split("-")[-1].split(".")[0])
        # g = sns.lineplot(data=data[data["Subject"].isin(range(1, 68))], x='Subject', y=metric, hue='Condition',
        #             hue_order=["Typical", "Parkinsons", "Comorbities", "Balance"])
        sns.lineplot(data=df[["AccZLeft", "AccYWrist"]])
        fpNonZero = df["FP1Z"][df["FP1Z"] != 0]
        fpNonZero = fpNonZero[fpNonZero.notna()].abs()
        # print(fpNonZero)
        # print(fpNonZero.max())
        fpNonZeroNormalised = fpNonZero.div(fpNonZero.max()) * 10
        # print(fpNonZeroNormalised)
        # print(df["FP1Z"].div(max(df["FP1Z"].to_numpy()), fill_value=0).mul(10, fill_value=0))
        sns.lineplot(data=fpNonZeroNormalised)
        plt.vlines(fpNonZeroNormalised.index[0], 0, 10, linestyles='solid', colors='r')
        plt.show()
