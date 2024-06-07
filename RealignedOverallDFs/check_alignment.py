import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

for subjectNum in [x for x in range(67, 68) if x not in [11, 20, 22, 24, 47, 48, 49]]:
    subjectNum2 = str(subjectNum).zfill(2)
    dataDir = "TF_{}/".format(subjectNum2)
    for file in os.listdir(dataDir):
        df = pd.read_csv(os.path.join(dataDir, file), usecols=["AccZLeft", "FP1Z", "FP2Z"])
        df[["FP1Z", "FP2Z"]] = df[["FP1Z", "FP2Z"]] / 100
        sns.lineplot(data=df)
        plt.title(file)
        plt.show()
