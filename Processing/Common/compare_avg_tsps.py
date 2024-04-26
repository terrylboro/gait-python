import os
import pandas as pd
from matplotlib import pyplot as plt

gtDir = "../../C3d/OwnGroundTruth/TSPs/"
diaoDir = "../Ear/Events/AdaptedDiao/TSPs/"

for file in os.listdir(gtDir)[25:27]:
    df = pd.read_csv(gtDir + file)
    if not df.empty:
        for column in range(0, 2):
            if not df.empty:
                data = df.iloc[:, column]#.values
                data.dropna(inplace=True)
                if column == 0:
                    q_low = data.quantile(0.25)
                    q_hi = data.quantile(0.75)
                    sortedVals = data.sort_values(ignore_index=True)
                    plt.plot(sortedVals, 'bo')
                    plt.hlines([q_low, q_hi], 0, 120)
                    plt.title(file)
                    plt.show()
                    # print(sortedVals[int(0.5*len(sortedVals)) - 2 : int(0.5*len(sortedVals)) + 2])
                    cutoff_hi = sortedVals[sortedVals < q_hi]
                    cutVals = cutoff_hi[cutoff_hi > q_low]
                    # print(cutVals)
                    avgVal = cutVals.mean()
                    print(avgVal)


        # print(df[["Left Stride Time", "Right Stride Time"]].median())

        # print(df.describe())

for file in os.listdir(diaoDir)[25:27]:
    df = pd.read_csv(diaoDir + file)
    if not df.empty:
        if not df.empty:
            for column in range(0, 2):
                if not df.empty:
                    data = df.iloc[:, column]  # .values
                    data.dropna(inplace=True)
                    if column == 0:
                        q_low = data.quantile(0.25)
                        q_hi = data.quantile(0.75)
                        sortedVals = data.sort_values(ignore_index=True)
                        plt.plot(sortedVals, 'ro')
                        plt.hlines([q_low, q_hi], 0, 120)
                        plt.title(file)
                        plt.show()
                        # print(sortedVals[int(0.5 * len(sortedVals)) - 2: int(0.5 * len(sortedVals)) + 2])
                        # avgVal = sortedVals[int(0.5 * len(sortedVals)) - 2: int(0.5 * len(sortedVals)) + 2].mean()
                        # print(avgVal)
                        cutoff_hi = sortedVals[sortedVals < q_hi]
                        cutVals = cutoff_hi[cutoff_hi > q_low]
                        # print(cutVals)
                        avgVal = cutVals.mean()
                        print(avgVal)
        # print(df[["Left Stride Time", "Right Stride Time"]].median())

