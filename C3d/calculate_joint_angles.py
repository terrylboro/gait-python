import os
import numpy as np
import pandas as pd
import pyc3dserver as c3d
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, butter, filtfilt, argrelmax
import json
import re


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
    try:
        fpArr = np.zeros((end_fr * 20, 6), dtype=np.float32)
        for i, idx in zip(range(6), [0, 1, 2, 6, 7, 8]):
            fpArr[(start_fr - 1) * 20:, i] = np.asarray(itf.GetAnalogDataEx(idx, start_fr, end_fr, '0', 0, 0, '0'),
                                                        dtype=np.float32)
    except ValueError:
        fpArr = np.zeros((end_fr * 10, 6), dtype=np.float32)
        for i, idx in zip(range(6), [0, 1, 2, 6, 7, 8]):
            fpArr[(start_fr - 1) * 10:, i] = np.asarray(itf.GetAnalogDataEx(idx, start_fr, end_fr, '1', 0, 0, '0'),
                                                        dtype=np.float32)
    # fpData = pd.DataFrame(data=fpArr, columns=['FP1X', 'FP1Y', 'FP1Z', 'FP2X', 'FP2Y', 'FP2Z'])
    # fpData[["FP1X", "FP2X"]].plot()
    # plt.show()
    return fpArr


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
    fpArr = get_fp_data(itf, start_fr, end_fr)

    # get marker data
    mkrTrajArr = get_marker_trajectories(itf, start_fr, end_fr)

    # concatenate these into 1 array (need to downsample force plate)
    opticalArr = np.concatenate((mkrTrajArr, fpArr[::20, :]), axis=1)

    # make this into a pandas df
    colNames = ["asisDataLX", "asisDataLY", "asisDataLZ", "asisDataRX", "asisDataRY", "asisDataRZ", \
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
    opticalDF.to_csv("opticalDF.csv", index=False)

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
        print(int(subject.split("_")[1]))
        subjectNum = int(subject.split("_")[1])
        if subjectNum in [61] :#[x for x in range(58, 68) if x not in [40, 41, 46, 47, 48, 61]]:
            filepath = subjectPath + subject + "/"
            for file in os.listdir(filepath):
                if file.endswith(".c3d"):
                    trialNum = int(file.split('_')[-1].split(".")[0])
                    print(trialNum)
                    if trialNum in [x for x in range(2, 10)]:
                        opticalDF = get_fp_and_marker_data(filepath+file)
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
                        print(kneeAngleL.shape)
                        print(len(opticalDF))
                        opticalDF[["ankleAngleL", "ankleAngleR", "kneeAngleL", "kneeAngleR"]] = np.concatenate((ankleAngleL, ankleAngleR, kneeAngleL, kneeAngleR), axis=1)
                        opticalDF.to_csv("{}-{}-opticalDF.csv".format(subjectNum, str(trialNum).zfill(2)), index=False)
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

