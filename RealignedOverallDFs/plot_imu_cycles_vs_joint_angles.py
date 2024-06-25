import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns

def normalise_arr(data, meanData):
    return (data - np.amin(meanData)) / (np.amax(meanData) - np.amin(meanData))

cyclesDF = pd.read_csv('../OverallDFs/gaitCycleDetails.csv')
jointAnglesDir = "../JointAngleDFs/"

for subjectNum in range(67, 68):
    # find the indices with full strikes
    leftSubjectCyclesDF = cyclesDF[cyclesDF.Subject == subjectNum]
    rightSubjectCyclesDF = cyclesDF[cyclesDF.Subject == subjectNum]
    leftSubjectCyclesDF = leftSubjectCyclesDF[leftSubjectCyclesDF.CycleSide == "Left"]
    rightSubjectCyclesDF = rightSubjectCyclesDF[rightSubjectCyclesDF.CycleSide == "Right"]
    leftSubjectCyclesDF = leftSubjectCyclesDF[leftSubjectCyclesDF.Activity == "Walk"]
    rightSubjectCyclesDF = rightSubjectCyclesDF[rightSubjectCyclesDF.Activity == "Walk"]
    leftSubjectCyclesDF = leftSubjectCyclesDF[leftSubjectCyclesDF.TrialNum != 11]
    rightSubjectCyclesDF = rightSubjectCyclesDF[rightSubjectCyclesDF.TrialNum != 11]
    leftSubjectCyclesDF = leftSubjectCyclesDF[["Subject", "TrialNum", "IC1", "FO2", "IC3"]]
    rightSubjectCyclesDF = rightSubjectCyclesDF[["Subject", "TrialNum", "IC1", "FO2", "IC3"]]
    print(rightSubjectCyclesDF)
    print(leftSubjectCyclesDF)

    # plot the force plate readings for each side
    for side in ["Left", "Right"]:
        subjectCyclesDF = leftSubjectCyclesDF if side == "Left" else rightSubjectCyclesDF
        indices = subjectCyclesDF.index.tolist()
        print(len(indices))
        kneeAngleArr = np.zeros((len(indices), 130))
        imuArr = np.zeros((len(indices), 130))
        for i in range(0, len(subjectCyclesDF)):
            trialNum = subjectCyclesDF.loc[indices[i], "TrialNum"].tolist()
            ic1 = subjectCyclesDF.loc[indices[i], "IC1"].tolist()
            fo2 = subjectCyclesDF.loc[indices[i], "IC3"].tolist()
            # load the time series data
            imuData = pd.read_csv('TF_{}/{}-{}.csv'.format(subjectNum, subjectNum, str(trialNum).zfill(2)), usecols=["AccZLeft", "AccZRight"])
            # print(imuData)
            jointData = pd.read_csv(os.path.join(jointAnglesDir, "A096391_67_{}.csv".format(str(trialNum).zfill(4))))
            # arrange the Angle data
            if side == "Left":
                kneeAngleData = jointData.LAnkleAnglesY.iloc[ic1:fo2 + 1]
            else:
                kneeAngleData = jointData.RAnkleAnglesY.iloc[ic1:fo2 + 1]
            kneeAngleData.reset_index(drop=True, inplace=True)
            kneeAngleArr[i, :len(kneeAngleData)] = kneeAngleData.to_numpy().reshape(1, -1)
            # arrange the IMU Data
            gaitCycle = imuData.AccZLeft.iloc[ic1:fo2 + 1]
            gaitCycle = gaitCycle.reset_index(drop=True)
            imuArr[i, :len(gaitCycle)] = gaitCycle.to_numpy().reshape(1, -1)
            # plt.plot(kneeAngleArr)
            # plt.show()
        # use this to check the data
        # for i in range(0, 25):
        #     plt.plot(kneeAngleArr[i, :])
        # plt.show()
        ########
        # np.savetxt("Knee Angle Arr.csv", kneeAngleArr, delimiter=",")
        # plt.show()
        meanAngleCycle = np.mean(kneeAngleArr, axis=0)
        meanAngleCycle = meanAngleCycle[meanAngleCycle != 0]
        maxAngleCycle = np.max(kneeAngleArr, axis=0)[:len(meanAngleCycle)]
        minAngleCycle = np.min(kneeAngleArr, axis=0)[:len(meanAngleCycle)]
        meanIMUCycle = np.mean(imuArr, axis=0)
        meanIMUCycle = meanIMUCycle[:len(meanAngleCycle)]
        maxIMUCycle = np.max(imuArr, axis=0)[:len(meanAngleCycle)]
        minIMUCycle = np.min(imuArr, axis=0)[:len(meanAngleCycle)]

        # Plot the data with min/max intervals filled in
        x = np.linspace(0, 100, len(meanAngleCycle))
        g = sns.lineplot(x=x, y=normalise_arr(meanAngleCycle, meanAngleCycle))
        plt.fill_between(x, normalise_arr(minAngleCycle, meanAngleCycle), normalise_arr(maxAngleCycle, meanAngleCycle), alpha=0.3)
        sns.lineplot(x=x, y=normalise_arr(meanIMUCycle, meanIMUCycle))
        plt.fill_between(x, normalise_arr(minIMUCycle, meanIMUCycle), normalise_arr(maxIMUCycle, meanIMUCycle), alpha=0.3)
        plt.title(r'Avg. Ankle Angle and Acceleration During Gait Cycle for Participant {} - {} Side'.format(subjectNum, side), wrap=True, fontsize=20)
        plt.xlabel("% of Gait Cycle", fontsize=12)
        plt.ylabel(r'Acceleration or Angle', fontsize=12)
        plt.legend(["Ankle Angle Mean", "Ankle Angle Min/Max Interval", "_",
                    "IMU Mean", "IMU Min/Max Interval", "_"], fontsize=8)
        sns.move_legend(g, "lower center", bbox_to_anchor=(0.5, -0.4), ncol=2)
        plt.tight_layout()
        plt.savefig("../IMU vs Ankle Angle Plots/{}-{}.png".format(str(subjectNum).zfill(2), side),bbox_inches='tight')
        plt.close("all")
        # plt.show()
