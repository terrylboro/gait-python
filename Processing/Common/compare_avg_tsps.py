import os
import pandas as pd
from matplotlib import pyplot as plt
from calculate_tsps import find_trial_nums

activity = "Walk"
gtDir = "../../C3d/OwnGroundTruth/TSPsWalksAndTurf/" + activity + "/"
# imuDir = "../Ear/Events/AdaptedDiao/TSPs/"
# imuDir = "../Shank/Events/Gyro/TSPs/"
imuDir = "../Chest/Events/McCamley/TSPs/"


# for subjectNum in [x for x in range(10, 65) if x not in [20, 22]]:
for subjectNum in [x for x in range(10, 56) if x not in [46, 47, 48]]:
    goodSubjects = open("../../Utils/goodTrials",
                        "r").read()
    if "," + str(subjectNum).zfill(2) in goodSubjects:
        validTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/{}/Right/".format(str(subjectNum).zfill(2), activity))
        validTrialNums = find_trial_nums(validTrialFiles)
        gtdf = pd.read_csv(gtDir + "{}.csv".format(str(subjectNum).zfill(2)))
        diaodf = pd.read_csv(imuDir + "{}.csv".format(str(subjectNum).zfill(2)))
        if not gtdf.empty:
            summaryDF = pd.DataFrame(columns=
                                   ["Trial", "Left Stride Time Shank", "Left Stride Time GT", "Left Stride Time Diff",
                                    "Left Stance Time Shank", "Left Stance Time GT", "Left Stance Time Diff",
                                    "Left Swing Time Shank", "Left Swing Time GT", "Left Swing Time Diff"])
            # plot by trial instead
            gtgrouped = gtdf.groupby("Trial")
            diaogrouped = diaodf.groupby("Trial")
            for gttrialdf, diaotrialdf in zip(gtgrouped, diaogrouped):
                gttrialdf[1].reset_index(inplace=True)
                diaotrialdf[1].reset_index(inplace=True)
                trialDF = pd.DataFrame(columns=
                                         ["Trial", "Left Stride Time Shank", "Left Stride Time GT", "Left Stride Time Diff",
                                          "Left Stance Time Shank", "Left Stance Time GT", "Left Stance Time Diff",
                                          "Left Swing Time Shank", "Left Swing Time GT", "Left Swing Time Diff"])
                for column in ["Left Stride Time", "Left Stance Time", "Left Swing Time"]:
                    gtdata = gttrialdf[1][column]  # .values
                    diaodata = diaotrialdf[1][column]  # .values
                    print(diaotrialdf[1]["Trial"])
                    print(gtdata)
                    gtdata.dropna(inplace=True)
                    diaodata.dropna(inplace=True)
                    trialDF["Trial"] = diaotrialdf[1]["Trial"]
                    trialDF[column+" Shank"] = diaodata
                    trialDF[column+" GT"] = gtdata
                    trialDF[column+" Diff"] = gtdata - diaodata
                    # q_low = data.quantile(0.25)
                    # q_hi = data.quantile(0.75)
                    sortedgtVals = gtdata.sort_values(ignore_index=True)
                    sorteddiaoVals = diaodata.sort_values(ignore_index=True)
                    # plt.plot(sortedgtVals, 'bo')
                    # plt.plot(sorteddiaoVals, 'rx')
                    # plt.plot(gtdata, 'bo')
                    # plt.plot(diaodata, 'rx')
                    # # plt.hlines([q_low, q_hi], 0, 120)
                    # plt.title("Participant: {} Activity: {} - {}".format(subjectNum, activity, column))
                    # plt.show()
                    # # print(sortedVals[int(0.5*len(sortedVals)) - 2 : int(0.5*len(sortedVals)) + 2])
                    # cutoff_hi = sortedVals[sortedVals < q_hi]
                    # cutVals = cutoff_hi[cutoff_hi > q_low]
                    # # print(cutVals)
                    # avgVal = cutVals.mean()
                    # print(avgVal)
                summaryDF = pd.concat([summaryDF, trialDF], ignore_index=True)
            summaryDF.to_csv("{}.csv".format(str(subjectNum).zfill(2)), index=False)
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

