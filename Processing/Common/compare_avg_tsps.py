import os
import pandas as pd
from matplotlib import pyplot as plt
from calculate_tsps import find_trial_nums

activity = "Walk"
gtDir = "../../C3d/OwnGroundTruth/TSPsWalksAndTurf/" + activity + "/"
diaoDir = "../Ear/Events/AdaptedDiao/TSPs/"


for subjectNum in range(30, 40):
    validTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/{}/Right/".format(str(subjectNum).zfill(2), activity))
    validTrialNums = find_trial_nums(validTrialFiles)
    gtdf = pd.read_csv(gtDir + "{}.csv".format(str(subjectNum).zfill(2)))
    diaodf = pd.read_csv(diaoDir + "{}.csv".format(str(subjectNum).zfill(2)))
    if not gtdf.empty:
        for column in ["Left Swing Time", "Right Swing Time"]:
            if not gtdf.empty:
                gtdata = gtdf[column]#.values
                diaodata = diaodf[column]#.values
                gtdata.dropna(inplace=True)
                diaodata.dropna(inplace=True)
                # q_low = data.quantile(0.25)
                # q_hi = data.quantile(0.75)
                sortedgtVals = gtdata.sort_values(ignore_index=True)
                sorteddiaoVals = diaodata.sort_values(ignore_index=True)
                plt.plot(sortedgtVals, 'bo')
                plt.plot(sorteddiaoVals, 'rx')
                # plt.hlines([q_low, q_hi], 0, 120)
                plt.title("Participant: {} Activity: {}".format(subjectNum, activity))
                plt.show()
                # # print(sortedVals[int(0.5*len(sortedVals)) - 2 : int(0.5*len(sortedVals)) + 2])
                # cutoff_hi = sortedVals[sortedVals < q_hi]
                # cutVals = cutoff_hi[cutoff_hi > q_low]
                # # print(cutVals)
                # avgVal = cutVals.mean()
                # print(avgVal)


        # print(df[["Left Stride Time", "Right Stride Time"]].median())

        # print(df.describe())

# for file in os.listdir(diaoDir)[34:35]:
#     df = pd.read_csv(diaoDir + file)
#     if not df.empty:
#         if not df.empty:
#             for column in range(0, 2):
#                 if not df.empty:
#                     data = df.iloc[:, column]  # .values
#                     data.dropna(inplace=True)
#                     if column == 0:
#                         q_low = data.quantile(0.25)
#                         q_hi = data.quantile(0.75)
#                         sortedVals = data.sort_values(ignore_index=True)
#                         plt.plot(sortedVals, 'ro')
#                         plt.hlines([q_low, q_hi], 0, 120)
#                         plt.title(file)
#                         plt.show()
#                         # print(sortedVals[int(0.5 * len(sortedVals)) - 2: int(0.5 * len(sortedVals)) + 2])
#                         # avgVal = sortedVals[int(0.5 * len(sortedVals)) - 2: int(0.5 * len(sortedVals)) + 2].mean()
#                         # print(avgVal)
#                         cutoff_hi = sortedVals[sortedVals < q_hi]
#                         cutVals = cutoff_hi[cutoff_hi > q_low]
#                         # print(cutVals)
#                         avgVal = cutVals.mean()
#                         print(avgVal)
#         # print(df[["Left Stride Time", "Right Stride Time"]].median())

