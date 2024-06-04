import os
import numpy as np
import pandas as pd
import pyc3dserver as c3d
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, butter, filtfilt, argrelmax
import json
import re
from Processing.Common.generic_imu_tilt_correct import generic_imu_tilt_correct


def hp_filter(data, freq):
    b, a = butter(2, freq, btype="high", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def lp_filter(data, freq):
    b, a = butter(2, freq, btype="low", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def bp_filter(data, freq1, freq2):
    b, a = butter(2, [freq1, freq2], btype="band", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]


def get_fp_data(itf, start_fr, end_fr):
    # load the forceplate data
    relSampleFreq = 20  # this is fp sampling freq / 100Hz. Usually 20 though sometimes 10
    try:
        fpArr = np.zeros((end_fr * relSampleFreq, 6), dtype=np.float32)
        for i, idx in zip(range(6), [0, 1, 2, 6, 7, 8]):
            fpArr[(start_fr - 1) * relSampleFreq:, i] = np.asarray(itf.GetAnalogDataEx(idx, start_fr, end_fr, '0', 0, 0, '0'),
                                                        dtype=np.float32)
    except ValueError:
        relSampleFreq = 10
        fpArr = np.zeros((end_fr * relSampleFreq, 6), dtype=np.float32)
        for i, idx in zip(range(6), [0, 1, 2, 6, 7, 8]):
            fpArr[(start_fr - 1) * relSampleFreq:, i] = np.asarray(itf.GetAnalogDataEx(idx, start_fr, end_fr, '1', 0, 0, '0'),
                                                        dtype=np.float32)
    # fpData = pd.DataFrame(data=fpArr, columns=['FP1X', 'FP1Y', 'FP1Z', 'FP2X', 'FP2Y', 'FP2Z'])
    # fpData[["FP1X", "FP2X"]].plot()
    # plt.show()
    return fpArr, relSampleFreq


def get_wrist_shank_data(itf, start_fr, end_fr):
    # find the IMU data indices from labels
    wristFirstIdx = c3d.get_analog_index(itf, "Sensor {} Acc.ACCX{}".format(1, 1))
    shankFirstIdx = c3d.get_analog_index(itf, "Sensor {} Acc.ACCX{}".format(2, 2))
    wristRange = range(wristFirstIdx, wristFirstIdx+6)
    shankRange = range(shankFirstIdx, shankFirstIdx+6)
    # use these indices to find the data
    relSampleFreq = 20  # this is Delsys sampling freq / 100Hz. Usually 20 though sometimes 10
    try:
        wristShankArr = np.zeros((end_fr * relSampleFreq, 12), dtype=np.float32)
        for sig_idx in wristRange:
            data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
            wristShankArr[(start_fr-1)*relSampleFreq:, sig_idx - wristRange[0]] = data
        for sig_idx in shankRange:
            data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
            wristShankArr[(start_fr-1)*relSampleFreq:, sig_idx - shankRange[0] + 6] = data
    except ValueError:
        relSampleFreq = 10
        wristShankArr = np.zeros((end_fr * relSampleFreq, 12), dtype=np.float32)
        for sig_idx in wristRange:
            data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
            wristShankArr[(start_fr - 1) * relSampleFreq:, sig_idx - wristRange[0]] = data
        for sig_idx in shankRange:
            data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
            wristShankArr[(start_fr - 1) * relSampleFreq:, sig_idx - shankRange[0] + 6] = data
    return wristShankArr, relSampleFreq


def get_fp_and_marker_data(filepath):
    """ 14 = RHEE 9 = LHEE """
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    end_fr = itf.GetVideoFrame(1)
    n_frs = end_fr - start_fr + 1

    # get fp data
    fpArr, fpRelFreq = get_fp_data(itf, start_fr, end_fr)

    # get marker data
    try:
        mkrTrajArr = get_marker_trajectories(itf, start_fr, end_fr)
    except:
        print("Markers not labelled")
        return False
    # get IMU data
    try:
        wristShankArr, wristShankRelFreq = get_wrist_shank_data(itf, start_fr, end_fr)
    except:
        print("No IMU data here")
        wristShankArr = np.zeros((len(fpArr), 12))
        wristShankRelFreq = fpRelFreq
    # wristShankArr[:, 0:6] = generic_imu_tilt_correct(wristShankArr[:, 0:6], "Wrist")
    # wristShankArr[:, 6:12] = generic_imu_tilt_correct(wristShankArr[:, 6:12], "Shank")

    # concatenate these into 1 array (need to downsample force plate)
    opticalArr = np.concatenate((wristShankArr[::wristShankRelFreq, :], mkrTrajArr, fpArr[::fpRelFreq, :]), axis=1)

    # make this into a pandas df
    colNames = ["AccXWrist", "AccYWrist", "AccZWrist", "GyroXWrist", "GyroYWrist", "GyroZWrist", \
                "AccXShank", "AccYShank", "AccZShank", "GyroXShank", "GyroYShank", "GyroZShank", \
                "asisDataLX", "asisDataLY", "asisDataLZ", "asisDataRX", "asisDataRY", "asisDataRZ", \
                "psisDataLX", "psisDataLY", "psisDataLZ", "psisDataRX", "psisDataRY", "psisDataRZ", \
                "thighDataLX", "thighDataLY", "thighDataLZ", "thighDataRX", "thighDataRY", "thighDataRZ", \
                "kneeDataLX", "kneeDataLY", "kneeDataLZ", "kneeDataRX", "kneeDataRY", "kneeDataRZ", \
                "heelDataLX", "heelDataLY", "heelDataLZ", "heelDataRX", "heelDataRY", "heelDataRZ", \
                "tibDataLX", "tibDataLY", "tibDataLZ", "tibDataRX", "tibDataRY", "tibDataRZ", \
                "ankDataLX", "ankDataLY", "ankDataLZ", "ankDataRX", "ankDataRY", "ankDataRZ", \
                "toeDataLX", "toeDataLY", "toeDataLZ", "toeDataRX", "toeDataRY", "toeDataRZ",\
                'FP1X', 'FP1Y', 'FP1Z', 'FP2X', 'FP2Y', 'FP2Z']

    # concatenate the two DFs
    opticalDF = pd.DataFrame(opticalArr, columns=colNames)
    # opticalDF.to_csv("opticalDF.csv", index=False)

    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return opticalDF


def get_marker_trajectories(itf, start_fr, end_fr):
    # find markers by label
    # right markers
    mkr_RASI = c3d.get_marker_index(itf, "RASI")
    mkr_RPSI = c3d.get_marker_index(itf, "RPSI")
    mkr_RTHI = c3d.get_marker_index(itf, "RTHI")
    mkr_RKNE = c3d.get_marker_index(itf, "RKNE")
    mkr_RTIB = c3d.get_marker_index(itf, "RTIB")
    mkr_RHEE = c3d.get_marker_index(itf, "RHEE")
    mkr_RANK = c3d.get_marker_index(itf, "RANK")
    mkr_RTOE = c3d.get_marker_index(itf, "RTOE")
    # left markers
    mkr_LASI = c3d.get_marker_index(itf, "LASI")
    mkr_LPSI = c3d.get_marker_index(itf, "LPSI")
    mkr_LTHI = c3d.get_marker_index(itf, "LTHI")
    mkr_LKNE = c3d.get_marker_index(itf, "LKNE")
    mkr_LTIB = c3d.get_marker_index(itf, "LTIB")
    mkr_LHEE = c3d.get_marker_index(itf, "LHEE")
    mkr_LANK = c3d.get_marker_index(itf, "LANK")
    mkr_LTOE = c3d.get_marker_index(itf, "LTOE")
    # array to hold the 3-axis data from each
    asisDataL = np.zeros((end_fr, 3), dtype=np.float32)
    asisDataR = np.zeros((end_fr, 3), dtype=np.float32)
    psisDataL = np.zeros((end_fr, 3), dtype=np.float32)
    psisDataR = np.zeros((end_fr, 3), dtype=np.float32)
    thighDataL = np.zeros((end_fr, 3), dtype=np.float32)
    thighDataR = np.zeros((end_fr, 3), dtype=np.float32)
    kneeDataL = np.zeros((end_fr, 3), dtype=np.float32)
    kneeDataR = np.zeros((end_fr, 3), dtype=np.float32)
    heelDataL = np.zeros((end_fr, 3), dtype=np.float32)
    heelDataR = np.zeros((end_fr, 3), dtype=np.float32)
    tibDataL = np.zeros((end_fr, 3), dtype=np.float32)
    tibDataR = np.zeros((end_fr, 3), dtype=np.float32)
    ankDataL = np.zeros((end_fr, 3), dtype=np.float32)
    ankDataR = np.zeros((end_fr, 3), dtype=np.float32)
    toeDataL = np.zeros((end_fr, 3), dtype=np.float32)
    toeDataR = np.zeros((end_fr, 3), dtype=np.float32)

    mkrLocList = [asisDataL, asisDataR, psisDataL, psisDataR, thighDataL, thighDataR,\
                   kneeDataL, kneeDataR, heelDataL, heelDataR, tibDataL, tibDataR,\
                   ankDataL, ankDataR, toeDataL, toeDataR]

    mkr_list = [mkr_LASI, mkr_RASI, mkr_LPSI, mkr_RPSI, mkr_LTHI, mkr_RTHI,\
                       mkr_LKNE, mkr_RKNE, mkr_LHEE, mkr_RHEE, mkr_LTIB, mkr_RTIB,\
                       mkr_LANK, mkr_RANK, mkr_LTOE, mkr_RTOE]

    for mkrLoc, mkr_NAME in zip(mkrLocList, mkr_list):
        for j in range(3):
            mkrLoc[(start_fr-1):, j] = np.asarray(itf.GetPointDataEx(mkr_NAME, j, start_fr, end_fr, '1'), dtype=np.float32)

    mkrTrajArr = np.concatenate(([x for x in mkrLocList]), axis=1)
    return mkrTrajArr


def get_walking_trial_nums(subjectNum):
    # load the activity info
    activityDF = pd.read_csv('../C3d/ActivitiesIndex.csv')
    subjectDF = activityDF[activityDF["SubjectNum"] == subjectNum]
    walkingTrialNums = []
    for col in subjectDF.columns:
        if not subjectDF[col].isnull().values.any() and col in ['Walk', 'WalkNod', 'WalkShake']:
            trialNumsForThisActivity = [int(x) for x in subjectDF[col].values[0][1:-1].split(",")]
            walkingTrialNums.extend(trialNumsForThisActivity)
    return walkingTrialNums


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            angle_between((1, 0, 0), (1, 0, 0))
            0.0
            angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def calculate_joint_angle(data):
    # 0 = TIB, 1 = ANK, 2 = TOE
    v1 = data[:, 0:3] - data[:, 3:6]
    v2 = data[:, 6:9] - data[:, 3:6]
    angle_arr = np.zeros((len(data), 1))
    for i in range(0, len(data)):
        angle_arr[i, 0] = angle_between(v1[i, :], v2[i, :])
    # angle_arr = angle_arr[~np.isnan(angle_arr)]
    angle_arr = angle_arr.reshape(len(angle_arr), 1)
    return np.rad2deg(angle_arr)


if __name__ == '__main__':
    subjectPath = "C:/Users/teri-/Documents/GaitC3Ds/"
    for subject in os.listdir(subjectPath):
        print(subject)
        subjectNum = int(subject.split("_")[1])
        if subjectNum in [x for x in range(51, 68) if x not in [11, 46, 47, 48]]:
            filepath = subjectPath + subject + "/"
            walkingTrialNums = get_walking_trial_nums(subjectNum)
            for file in os.listdir(filepath):
                if file.endswith(".c3d"):
                    trialNum = int(file.split('_')[-1].split(".")[0])
                    print(trialNum)
                    if trialNum in walkingTrialNums:
                        opticalDF = get_fp_and_marker_data(filepath + file)
                        if type(opticalDF) == pd.DataFrame:
                            ankleAngleL = calculate_joint_angle(
                                opticalDF[["tibDataLX", "tibDataLY", "tibDataLZ",\
                                           "heelDataLX", "heelDataLY", "heelDataLZ",\
                                           "toeDataLX", "toeDataLY", "toeDataLZ"]].to_numpy()
                            )
                            ankleAngleR = calculate_joint_angle(
                                opticalDF[["tibDataRX", "tibDataRY", "tibDataRZ", \
                                           "heelDataRX", "heelDataRY", "heelDataRZ", \
                                           "toeDataRX", "toeDataRY", "toeDataRZ"]].to_numpy()
                            )
                            kneeAngleL = calculate_joint_angle(
                                opticalDF[["thighDataLX", "thighDataLY", "thighDataLZ",\
                                           "kneeDataLX", "kneeDataLY", "kneeDataLZ",\
                                           "tibDataLX", "tibDataLY", "tibDataLZ"]].to_numpy()
                            )
                            kneeAngleR = calculate_joint_angle(
                                opticalDF[["thighDataRX", "thighDataRY", "thighDataRZ", \
                                           "kneeDataRX", "kneeDataRY", "kneeDataRZ", \
                                           "tibDataRX", "tibDataRY", "tibDataRZ"]].to_numpy()
                            )
                            opticalDF[["ankleAngleL", "ankleAngleR", "kneeAngleL", "kneeAngleR"]] = np.concatenate((ankleAngleL, ankleAngleR, kneeAngleL, kneeAngleR), axis=1)
                            opticalDF.to_csv("../OpticalDFs/TF_{}/{}-{}.csv".format(
                                str(subjectNum).zfill(2), str(subjectNum).zfill(2), str(trialNum).zfill(2)), index=False)
                            # opticalDF[["ankleAngleL", "ankleAngleR", "kneeAngleL", "kneeAngleR"]].plot()
                            # opticalDF[["FP1Z", "FP2Z"]] -= opticalDF[["FP1Z", "FP2Z"]].min()
                            # opticalDF[["FP1Z", "FP2Z"]] /= opticalDF[["FP1Z", "FP2Z"]].max()
                            # plt.plot((opticalDF[["FP1Z", "FP2Z"]] * -200) + 200)
                            # plt.title(trialNum)
                            # plt.show()

    # imuDF = pd.read_csv("../AlignedData/TF_61/61-02.csv")
    # imuDF = imuDF.iloc[1:339, :]
    # print(imuDF.shape)
    # opticalDF = pd.read_csv("opticalDF.csv")
    # print(opticalDF.shape)
    # # plt.plot(opticalDF[["FP1Z", "FP2Z"]])
    # plt.plot(imuDF[["AccZlear", "AccZpocket"]] * 10)
    # plt.show()

