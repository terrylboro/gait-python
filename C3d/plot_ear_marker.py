import os
import numpy as np
import pandas as pd
import pyc3dserver as c3d
import seaborn as sns
import matplotlib.pyplot as plt
from C3d.find_gait_event_optical import lp_filter

for subjectNum in range(61, 62):
    subjectNum2 = str(subjectNum).zfill(2)
    for trialNum in range(6, 7):
        trialNum2 = str(trialNum).zfill(2)
        trialNum4 = str(trialNum).zfill(4)
        filepath = "C:/Users/teri-/Documents/GaitC3Ds/TF_{}/TF_{}_{}.c3d".format(subjectNum2, subjectNum2, trialNum4)
        # Get the COM object of C3Dserver
        itf = c3d.c3dserver()
        # Open a C3D file
        ret = c3d.open_c3d(itf, filepath)
        # Determine start and end frame numbers (to compensate for cropping)
        start_fr = itf.GetVideoFrame(0)
        end_fr = itf.GetVideoFrame(1)
        n_frs = end_fr - start_fr + 1

        # find markers by label
        mkr_LEAR = c3d.get_marker_index(itf, "*18")
        learTraj = np.zeros((end_fr, 3), dtype=np.float32)
        d2ydx2 = np.zeros((end_fr), dtype=np.float32)
        for j in range(3):
            learTraj[(start_fr - 1):, j] = np.asarray(itf.GetPointDataEx(mkr_LEAR, j, start_fr, end_fr, '1'), dtype=np.float32)

        # find derivatives and plot the acceleration
        y = learTraj[(start_fr - 1):, 2]
        x = np.arange(y.size)
        dydx = np.gradient(y, x)
        d2ydx2[(start_fr - 1):] = np.gradient(dydx, x)
        d2ydx2 = (d2ydx2 - min(d2ydx2)) / max(d2ydx2 - min(d2ydx2))
        # d2ydx2 = np.insert(d2ydx2, 0, np.zeros(firstNonZeroVal))
        print("d2ydx2: ", len(d2ydx2))
        g = sns.lineplot(data=lp_filter(d2ydx2, 40), label="Marker Acc")
        # plt.show()

        # compare this to the ear signal
        imuDF = pd.read_csv("../IMUSystemData/TF_{}/TF_{}-{}.csv".format(subjectNum2, subjectNum2, trialNum2))
        imuDF = imuDF.AccZLeft[imuDF.AccZLeft != 0].shift(-6)
        # imuDF = imuDF.AccZRight[imuDF.AccZRight != 0].shift(-10)
        sns.lineplot(data=imuDF / imuDF.max(), label="IMU Acc")
        # plt.show()

        # # also compare to the forceplate
        # fpData = pd.read_csv("../OpticalDFs/TF_57/57-03.csv")
        # fp1Data = fpData.FP1Z * -1 #[fpData.FP1Z < 0] * -1
        # fp1Data = fp1Data.div(fp1Data.max())#.shift(-firstNonZeroVal)
        # fp2Data = fpData.FP2Z * -1  # [fpData.FP1Z < 0] * -1
        # fp2Data = fp2Data.div(fp2Data.max())  # .shift(-firstNonZeroVal)

        # from the c3d
        relSamplingFreq = 20
        fp1 = np.zeros((end_fr * relSamplingFreq), dtype=np.float32)
        fp2 = np.zeros((end_fr * relSamplingFreq), dtype=np.float32)

        fp1[(start_fr - 1) * relSamplingFreq:] = np.asarray(itf.GetAnalogDataEx(2, start_fr, end_fr, '1', 0, 0, '0'),
                                                dtype=np.float32)
        fp2[(start_fr - 1) * relSamplingFreq:] = np.asarray(itf.GetAnalogDataEx(8, start_fr, end_fr, '1', 0, 0, '0'),
                                                dtype=np.float32)


        print("fp1: ", len(fp1[::relSamplingFreq]))
        print("fp2: ", len(fp2[::relSamplingFreq]))
        fp1 = -fp1[::relSamplingFreq]/ max(-fp1[::relSamplingFreq])
        fp1[fp1 < 0] = 0
        fp2 = -fp2[::relSamplingFreq]/ max(-fp2[::relSamplingFreq])
        fp2[fp2 < 0] = 0
        sns.lineplot(data=fp1, label="FP 1")
        sns.lineplot(data=fp2, label="FP 2")
        fp1Impact = next((i for i, j in enumerate(fp1 > 0.1) if j), None)
        fp2Impact = next((i for i, j in enumerate(fp2 > 0.1) if j), None)
        fp1FOArr = fp1[fp1Impact:]
        fp2FOArr = fp2[fp2Impact:]
        fp1Off = next((i for i, j in enumerate(fp1FOArr > 0.1) if not j), None)
        fp2Off = next((i for i, j in enumerate(fp2FOArr > 0.1) if not j), None)
        # print((fp1 > 0.1))
        plt.vlines([fp1Impact, fp2Impact], 0, 1, linestyles='dotted')
        plt.vlines([fp1Off + fp1Impact, fp2Off + fp2Impact], 0, 1, linestyles='dotted', color='purple')
        g.set_xlabel("Time * 10 / ms")
        g.set_ylabel("Normalised Acceleration or Force")
        g.set_title("Ear IMU and Marker Accelerations with FP Data: {}-{}".format(subjectNum2, trialNum2))
        sns.move_legend(g, "lower center", bbox_to_anchor=(0.5, -0.25), ncol=4)
        plt.tight_layout()
        plt.savefig("../IMU vs Ear Marker Plots/{}-{}.png".format(subjectNum2, trialNum2))
        plt.show()
