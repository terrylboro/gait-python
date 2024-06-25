import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns


def normalise_arr(data, meanData):
    return (data - np.amin(meanData)) / (np.amax(meanData) - np.amin(meanData))


plotNormalised = False  # toggle to true to plot normalised vals
participantMass = 72

cyclesDF = pd.read_csv('../OverallDFs/gaitCycleDetails.csv')
for subjectNum in [x for x in range(1, 56) if x not in [20, 22, 24, 45, 46, 47]]:
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
        leftSubjectCyclesDF = leftSubjectCyclesDF[["Subject", "TrialNum", "IC1", "FO2", "IC3", "IsFullFP1Strike", "IsFullFP2Strike"]]
        rightSubjectCyclesDF = rightSubjectCyclesDF[["Subject", "TrialNum", "IC1", "FO2", "IC3", "IsFullFP1Strike", "IsFullFP2Strike"]]
        print(rightSubjectCyclesDF)
        print(leftSubjectCyclesDF)

        # plot the force plate readings for each side
        for side in ["Left", "Right"]:
            subjectCyclesDF = leftSubjectCyclesDF if side == "Left" else rightSubjectCyclesDF
            indices = subjectCyclesDF.index.tolist()
            fpArr = np.zeros((len(indices), 100))
            imuArr = np.zeros((len(indices), 100))
            for i in range(0, len(subjectCyclesDF)):
                trialNum = subjectCyclesDF.loc[indices[i], "TrialNum"].tolist()
                # if trialNum != 2:
                ic1 = subjectCyclesDF.loc[indices[i], "IC1"].tolist()
                fo2 = subjectCyclesDF.loc[indices[i], "FO2"].tolist()
                print("IC1:", ic1)
                print("FO2", fo2)
                # load the time series data
                fpData = pd.read_csv('TF_{}/{}-{}.csv'.format(str(subjectNum).zfill(2), str(subjectNum).zfill(2), str(trialNum).zfill(2)),
                                     usecols=["AccXLeft", "AccYLeft", "AccZLeft", "AccXRight", "AccYRight", "AccZRight",
                                              "FP1Z", "FP2Z"])
                # arrange the fp data
                forcePlateData1 = fpData.FP1Z.iloc[ic1 - 2:fo2]  # * -1
                if forcePlateData1.mean() < 0:
                    forcePlateData1 *= -1
                forcePlateData1.reset_index(drop=True, inplace=True)
                forcePlateData2 = fpData.FP2Z.iloc[ic1 - 2:fo2]
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
                # if len(forcePlateData1[forcePlateData1 == 0]) <  len(forcePlateData2[forcePlateData2 == 0]):
                #     print("Contact on FP1 on trial" + str(trialNum))
                #     forcePlateData1 = forcePlateData1[forcePlateData1 > 0]
                #     print(forcePlateData1.to_numpy().reshape(1, -1).shape)
                #     print(fpArr.shape)
                #     fp1Data = forcePlateData1.to_numpy().reshape(1, -1)
                #     fpArr[i, :len(forcePlateData1)] = fp1Data
                # else:
                #     print("Contact on FP2 on trial" + str(trialNum))
                #     forcePlateData2 = forcePlateData2[forcePlateData2 > 0]
                #     print(forcePlateData2.to_numpy().shape)
                #     fpArr[i, :len(forcePlateData2)] = forcePlateData2.to_numpy().reshape(1, -1)
                #     # plt.plot(forcePlateData2)

                # arrange the IMU Data
                gaitCycle = fpData.AccZRight.iloc[ic1:fo2 + 1]
                gaitCycle = gaitCycle.reset_index(drop=True)
                imuArr[i, :len(gaitCycle)] = gaitCycle.to_numpy().reshape(1, -1)

            # fpArr = fpArr[1: :]
            # imuArr = imuArr[1:, :]
            print(fpArr)
            print(imuArr)
            meanFPCycle = np.nanmean(fpArr, axis=0)
            meanFPCycle = meanFPCycle[meanFPCycle > 0]
            maxFPCycle = np.nanmax(fpArr, axis=0)[:len(meanFPCycle)]
            minFPCycle = np.nanmin(fpArr, axis=0)[:len(meanFPCycle)]
            meanIMUCycle = np.nanmean(imuArr, axis=0)
            meanIMUCycle = meanIMUCycle[:len(meanFPCycle)]
            maxIMUCycle = np.nanmax(imuArr, axis=0)[:len(meanFPCycle)]
            minIMUCycle = np.nanmin(imuArr, axis=0)[:len(meanFPCycle)]

            # Plot the data with min/max intervals filled in
            x = np.linspace(0, len(meanFPCycle) / 100, len(meanFPCycle))
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
                plt.title(r'Avg. Vertical Acceleration During Gait Cycle for Participant {} - {} Side'.format(
                    subjectNum, side), wrap=True, fontsize=20)
                plt.xlabel("Time / s", fontsize=12)
                plt.ylabel(r'Acceleration / $ms^{-2}$', fontsize=12)
                plt.legend(["Mass-Normalised Force Plate Mean", "Mass-Normalised Force Plate Min/Max Interval", "_",
                            "IMU Mean", "IMU Min/Max Interval", "_"], fontsize=8)
                sns.move_legend(g, "upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
                plt.tight_layout()
                plt.savefig("../IMU vs Forceplate Plots/Mass Adjusted {}-{}.png".format(str(subjectNum).zfill(2), side),bbox_inches='tight')
                plt.close("all")
                # plt.show()
    except:
        print("Error on this participant")

