import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns


def normalise_arr(data, meanData):
    return (data - np.amin(meanData)) / (np.amax(meanData) - np.amin(meanData))


def equalise_sample_lengths(arr):
    for i in range(0, arr.shape[0]):
        # create temporary cropped array
        temparr = arr[i, :]
        temparr = temparr[temparr != 0]
        # interpolate this to max length
        interptemparr = np.interp(np.linspace(0, 1, arr.shape[1]),
                                    np.linspace(0, 1, temparr.shape[0]), temparr)
        arr[i, :] = interptemparr
    return arr


plotNormalised = False  # toggle to true to plot normalised vals
# load masses and heights in df
participantInfo = pd.read_csv("../Utils/participantInfo.csv", index_col=0)

cyclesDF = pd.read_csv('../OverallDFs/gaitCycleDetails.csv')
for subjectNum in [x for x in range(1, 67) if x not in [11, 20, 22, 24, 45, 46, 47, 65, 66]]:
    try:
        # find the indices with full strikes
        leftSubjectCyclesDF = cyclesDF[np.logical_and(cyclesDF.Subject == subjectNum,
                                                  np.logical_or(cyclesDF.IsFullFP1Strike, cyclesDF.IsFullFP2Strike))]
        rightSubjectCyclesDF = cyclesDF[np.logical_and(cyclesDF.Subject == subjectNum,
                                                  np.logical_or(cyclesDF.IsFullFP1Strike, cyclesDF.IsFullFP2Strike))]
        leftSubjectCyclesDF = leftSubjectCyclesDF[leftSubjectCyclesDF.CycleSide == "Left"]
        rightSubjectCyclesDF = rightSubjectCyclesDF[rightSubjectCyclesDF.CycleSide == "Right"]
        leftSubjectCyclesDF = leftSubjectCyclesDF[leftSubjectCyclesDF.Activity == "Walk"]
        rightSubjectCyclesDF = rightSubjectCyclesDF[rightSubjectCyclesDF.Activity == "Walk"]
        # leftSubjectCyclesDF = leftSubjectCyclesDF[["Subject", "TrialNum", "IC1", "FO2", "IC3", "IsFullFP1Strike", "IsFullFP2Strike"]]
        # rightSubjectCyclesDF = rightSubjectCyclesDF[["Subject", "TrialNum", "IC1", "FO2", "IC3", "IsFullFP1Strike", "IsFullFP2Strike"]]
        leftSubjectCyclesDF = leftSubjectCyclesDF[
            ["Subject", "TrialNum", "FO1", "IC2", "IC3", "IsFullFP1Strike", "IsFullFP2Strike"]]
        rightSubjectCyclesDF = rightSubjectCyclesDF[
            ["Subject", "TrialNum", "FO1", "IC2", "IC3", "IsFullFP1Strike", "IsFullFP2Strike"]]
        print(rightSubjectCyclesDF)
        print(leftSubjectCyclesDF)
        participantMass = participantInfo.loc[subjectNum, "Mass"]

        # plot the force plate readings for each side
        for direction in ["X", "Y", "Z"]:
            for side in ["Left", "Right"]:
                subjectCyclesDF = leftSubjectCyclesDF if side == "Left" else rightSubjectCyclesDF
                indices = subjectCyclesDF.index.tolist()
                fpArr = np.zeros((len(indices), 100))
                imuArr = np.zeros((len(indices), 100))
                for i in range(0, len(subjectCyclesDF)):
                    trialNum = subjectCyclesDF.loc[indices[i], "TrialNum"].tolist()
                    # if trialNum != 2:
                    # uncomment for full stance phase
                    # ic1 = subjectCyclesDF.loc[indices[i], "IC1"].tolist()
                    # fo2 = subjectCyclesDF.loc[indices[i], "FO2"].tolist()
                    # uncomment for single-leg support only
                    ic1 = subjectCyclesDF.loc[indices[i], "FO1"].tolist()
                    fo2 = subjectCyclesDF.loc[indices[i], "IC2"].tolist()
                    print("IC1:", ic1)
                    print("FO2", fo2)
                    # load the time series data
                    fpData = pd.read_csv('TF_{}/{}-{}.csv'.format(str(subjectNum).zfill(2), str(subjectNum).zfill(2), str(trialNum).zfill(2)),
                                         usecols=["AccXLeft", "AccYLeft", "AccZLeft", "AccXRight", "AccYRight", "AccZRight",
                                                  "FP1X", "FP1Y", "FP1Z", "FP2X", "FP2Y", "FP2Z"])
                    # load fp data in wanted direction
                    if direction == "X":
                        forcePlateData1 = fpData.FP1Z.iloc[ic1:fo2 + 1]  # * -1
                        forcePlateData2 = fpData.FP2Z.iloc[ic1:fo2 + 1]
                        gaitCycle = fpData[["AccXLeft", "AccXRight"]].iloc[ic1:fo2 + 1].mean(axis=1)
                        gaitCycle = gaitCycle.reset_index(drop=True)
                        imuArr[i, :len(gaitCycle)] = gaitCycle.to_numpy().reshape(1, -1)
                    elif direction == "Y":
                        forcePlateData1 = fpData.FP1Y.iloc[ic1:fo2 + 1]  # * -1
                        forcePlateData2 = fpData.FP2Y.iloc[ic1:fo2 + 1]
                        gaitCycle = fpData[["AccYLeft", "AccYRight"]].iloc[ic1:fo2 + 1].mean(axis=1)
                        gaitCycle = gaitCycle.reset_index(drop=True)
                        imuArr[i, :len(gaitCycle)] = gaitCycle.to_numpy().reshape(1, -1)
                    else:
                        forcePlateData1 = fpData.FP1Z.iloc[ic1:fo2 + 1]  # * -1
                        forcePlateData2 = fpData.FP2Z.iloc[ic1:fo2 + 1]
                        gaitCycle = fpData[["AccZLeft", "AccZRight"]].iloc[ic1:fo2 + 1].mean(axis=1)
                        gaitCycle = gaitCycle.reset_index(drop=True)
                        imuArr[i, :len(gaitCycle)] = gaitCycle.to_numpy().reshape(1, -1)
                    # allow for force plate flipping
                    if forcePlateData1.mean() < 0:
                        forcePlateData1 *= -1
                    forcePlateData1.reset_index(drop=True, inplace=True)
                    if forcePlateData2.mean() < 0:
                        forcePlateData2 *= -1
                    forcePlateData2.reset_index(drop=True, inplace=True)
                    # use fact we know fp1 and fp2 now
                    if subjectCyclesDF.loc[indices[i], "IsFullFP1Strike"].tolist():
                        forcePlateData1 = forcePlateData1[forcePlateData1 > 0]
                        fp1Data = forcePlateData1.to_numpy().reshape(1, -1)
                        fpArr[i, :len(forcePlateData1)] = fp1Data
                    else:
                        forcePlateData2 = forcePlateData2[forcePlateData2 > 0]
                        fpArr[i, :len(forcePlateData2)] = forcePlateData2.to_numpy().reshape(1, -1)

                    # arrange the IMU Data
                    # gaitCycle = fpData.AccZRight.iloc[ic1:fo2 + 1]
                    # gaitCycle = gaitCycle.reset_index(drop=True)
                    # try some sort of avg of left and right IMU (more info !!!!)
                    # gaitCycle = fpData[["AccYLeft", "AccYRight"]].iloc[ic1:fo2 + 1].mean(axis=1)
                    # gaitCycle = gaitCycle.reset_index(drop=True)
                    # imuArr[i, :len(gaitCycle)] = gaitCycle.to_numpy().reshape(1, -1)

                # resample IMU and force plate arrays to ensure length is consistent
                fpArr = fpArr[:, ~np.all(fpArr == 0, axis=0)]
                imuArr = imuArr[:, :fpArr.shape[1]]
                fpArr = equalise_sample_lengths(fpArr)
                imuArr = equalise_sample_lengths(imuArr)

                meanFPCycle = np.nanmean(fpArr, axis=0)
                meanFPCycle = meanFPCycle[meanFPCycle > 0]
                maxFPCycle = np.nanmax(fpArr, axis=0)#[:len(meanFPCycle)]
                minFPCycle = np.nanmin(fpArr, axis=0)#[:len(meanFPCycle)]
                meanIMUCycle = np.nanmean(imuArr, axis=0)
                meanIMUCycle = meanIMUCycle#[:len(meanFPCycle)]
                maxIMUCycle = np.nanmax(imuArr, axis=0)#[:len(meanFPCycle)]
                minIMUCycle = np.nanmin(imuArr, axis=0)#[:len(meanFPCycle)]

                # Plot the data with min/max intervals filled in
                x = np.linspace(0, len(meanFPCycle), len(meanFPCycle))
                if plotNormalised:
                    g = sns.lineplot(x=x, y=normalise_arr(meanFPCycle, meanFPCycle))
                    plt.fill_between(x, normalise_arr(minFPCycle, meanFPCycle),
                                     normalise_arr(maxFPCycle, meanFPCycle), alpha=0.3)
                    sns.lineplot(x=x, y=normalise_arr(meanIMUCycle, meanIMUCycle))
                    plt.fill_between(x, normalise_arr(minIMUCycle, meanIMUCycle),
                                     normalise_arr(maxIMUCycle, meanIMUCycle), alpha=0.3)
                    plt.title(r'Avg. Vertical Force and Acceleration During Gait Cycle for Participant {} - {} Side'.format(subjectNum, side), wrap=True, fontsize=20)
                    plt.xlabel("Time / s", fontsize=12)
                    plt.ylabel(r'Normalised Acceleration or Force', fontsize=12)
                    plt.legend(["Force Plate Mean", "Force Plate Min/Max Interval", "_",
                                "IMU Mean", "IMU Min/Max Interval", "_"], fontsize=8)
                    sns.move_legend(g, "upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
                    plt.tight_layout()
                    # plt.savefig("../IMU vs Forceplate Plots/{}-{}.png".format(str(subjectNum).zfill(2), side),bbox_inches='tight')
                    # plt.close("all")
                    plt.show()
                else:
                    g = sns.lineplot(x=x, y=meanFPCycle / participantMass)
                    plt.fill_between(x, minFPCycle / participantMass, maxFPCycle / participantMass, alpha=0.3)
                    sns.lineplot(x=x, y=meanIMUCycle)
                    plt.fill_between(x, minIMUCycle, maxIMUCycle, alpha=0.3)
                    plt.title(r'Avg. {} Acceleration During Gait Cycle for Participant {} - {} Side'.format(
                        direction, subjectNum, side), wrap=True, fontsize=20)
                    plt.xlabel("Time / s", fontsize=12)
                    plt.ylabel(r'Acceleration / $ms^{-2}$', fontsize=12)
                    plt.legend(["Mass-Normalised Force Plate Mean", "Mass-Normalised Force Plate Min/Max Interval", "_",
                                "IMU Mean", "IMU Min/Max Interval", "_"], fontsize=8)
                    sns.move_legend(g, "upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
                    plt.tight_layout()
                    plt.savefig("../IMU vs Forceplate Plots XYZ/{}-{}-{}.png".format(str(subjectNum).zfill(2), direction, side),bbox_inches='tight')
                    plt.close("all")
                    # plt.show()
    except:
        print("Error on this participant")

