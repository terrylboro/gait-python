import os
import pandas as pd

gtDir = "../../C3d/OwnGroundTruth/TSPs/"
diaoDir = "../Ear/eVENTS/AdaptedDiao/TSPs/"

for file in os.listdir(gtDir)[25:26]:
    df = pd.read_csv(gtDir + file)
    if not df.empty:
        for column in range(0, 2):
            if not df.empty:
                data = df.iloc[:, column]#.values
                data.dropna(inplace=True)
                if column == 0:
                    sortedVals = data.sort_values(ignore_index=True)
                    print(sortedVals[int(0.5*len(sortedVals)) - 2 : int(0.5*len(sortedVals)) + 2])
                    avgVal = sortedVals[int(0.5*len(sortedVals)) - 2 : int(0.5*len(sortedVals)) + 2].mean()
                    print(avgVal)


        # print(df[["Left Stride Time", "Right Stride Time"]].median())

        # print(df.describe())

for file in os.listdir(diaoDir)[20:21]:
    df = pd.read_csv(diaoDir + file)
    if not df.empty:
        if not df.empty:
            for column in range(0, 2):
                if not df.empty:
                    data = df.iloc[:, column]  # .values
                    data.dropna(inplace=True)
                    if column == 0:
                        sortedVals = data.sort_values(ignore_index=True)
                        print(sortedVals[int(0.5 * len(sortedVals)) - 2: int(0.5 * len(sortedVals)) + 2])
                        avgVal = sortedVals[int(0.5 * len(sortedVals)) - 2: int(0.5 * len(sortedVals)) + 2].mean()
                        print(avgVal)
        # print(df[["Left Stride Time", "Right Stride Time"]].median())

