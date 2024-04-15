import os

import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
import json


def hp_filter(data, freq):
    b, a = butter(2, freq, btype="high", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def bp_filter(data, freq1, freq2):
    b, a = butter(2, [freq1, freq2], btype="band", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]

def get_heel_trajectory(filepath):
    """ 14 = RHEE 9 = LHEE """
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    end_fr = itf.GetVideoFrame(1)
    n_frs = end_fr - start_fr + 1

    mkr_RHEE = c3d.get_marker_index(itf, "RHEE")
    mkr_LHEE = c3d.get_marker_index(itf, "LHEE")

    fp_1 = np.zeros((end_fr * 20), dtype=np.float32)
    fp_2 = np.zeros((end_fr * 20), dtype=np.float32)

    fp_1[(start_fr-1) * 20:] = np.asarray(itf.GetAnalogDataEx(2, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    fp_2[(start_fr-1) * 20:] = np.asarray(itf.GetAnalogDataEx(8, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    heel_data_l = np.zeros((end_fr, 3), dtype=np.float32)
    heel_data_r = np.zeros((end_fr, 3), dtype=np.float32)
    for j in range(3):
        # try:
        heel_data_l[(start_fr-1):, j] = np.asarray(itf.GetPointDataEx(mkr_LHEE, j, start_fr, end_fr, '1'), dtype=np.float32)
        heel_data_r[(start_fr-1):, j] = np.asarray(itf.GetPointDataEx(mkr_RHEE, j, start_fr, end_fr, '1'), dtype=np.float32)
        # except:
        #     print("No heel data")


    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return heel_data_l, heel_data_r, fp_1, fp_2, (start_fr-1)


def IC_from_fp(fp_data):
    return int(round(np.where(fp_data < -10)[0][0] / 20)-1)

def autocorr(x):
    # x = hp_filter(x, 0.1)
    result = np.correlate(x, x, mode='full')
    return result[result.size // 2:]


def IC_from_heel(heel_data):
    # # original method using scipy peaks
    # # issue is setting thresholds
    # max_peaks = find_peaks(heel_data, prominence=15)[0]
    # print(max_peaks)
    # ICs = []
    # for peak in max_peaks:
    #     ICs.append(int(np.argmin(heel_data[peak:peak+50]) + peak))
    min_val = np.argmin(heel_data)
    # find the autocorrelation peaks
    peak_vals = find_peaks(autocorr(heel_data.flatten()))
    print(peak_vals)
    print(np.diff(peak_vals))
    # return ICs

def find_min_z(heel_data):
    heel_data = heel_data[~np.all(heel_data == 0)]
    minVal = np.argmin(heel_data)
    # find the autocorrelation peaks
    peakVals = find_peaks(autocorr(heel_data.flatten()))
    print(peakVals)
    # map the min_val to the position in the gait cycle
    min_val_cycle_num, minValIndexNum = find_nearest(peakVals[0], minVal)
    minOffsetVal = minVal - minValIndexNum
    HCList = []
    for peakVal in peakVals[0]:
        print(peakVal + minOffsetVal)
        firstEst = peakVal + minOffsetVal
        # accurateEst = np.argmin(heel_data.flatten()[firstEst-5:firstEst+5]) + (firstEst - 5)
        HCList.append(firstEst)
    # plt.plot(autocorr(heel_data.flatten()))
    # plt.show()
    return HCList

def freq_based_peak(heel_data_l, offset):
    ultraHP = bp_filter(heel_data_l[offset:, 2], 12, 25)
    plt.plot(np.square(ultraHP))
    ultraHPPeaks, _ = find_peaks(np.square(ultraHP), prominence=1.5, distance=70)
    plt.plot(ultraHPPeaks, np.square(ultraHP[ultraHPPeaks]), 'x')
    plt.show()
    plt.plot(heel_data_l[offset:, 2])
    plt.plot(ultraHPPeaks, heel_data_l[ultraHPPeaks, 2], 'x')
    plt.show()

def send_to_json(LHC, RHC, trial, subjectDict):
    subjectDict[trial] = {
        "LHC": LHC,
        "RHC": RHC
    }


def main():
    # filepath = "C:/Users/teri-/Documents/GaitC3Ds/A096391_58/A096391_58_0009.c3d"
    # Create json file for given subject
    subjectPath = "C:/Users/teri-/Documents/GaitC3Ds/"
    for subject in os.listdir(subjectPath): #[1:]:
    # for subject in ["TF_52", "TF_53", "TF_54"]:  # [1:]:
        print(subject)
        if int(subject.split("_")[1]) not in [2, 3, 4, 5, 16, 20] and int(subject.split("_")[1]) > 23:
        # if int(subject.split("_")[1]) in [10]:
            filepath = subjectPath + subject + "/"
            subjectDict = {}
            for file in os.listdir(filepath):
                if file.endswith(".c3d"):
                    trial = file.split('_')[-1].split(".")[0]
                    print(trial)
                    if int(trial) != 1:
                        heel_data_l, heel_data_r, fp_1, fp_2, offset = get_heel_trajectory(filepath + file)
                        # remove rows having all zeroes

                        # print("Min point is: {}".format(find_min_z(heel_data_l[offset:, 2])))
                        # HCList = find_min_z(heel_data_l[offset:, 2])
                        # plt.plot(heel_data_l[offset:, 2])
                        # plt.vlines(HCList, 0, 200)
                        # plt.show()
                        l_ICs, _ = find_peaks(-heel_data_l[offset:, 2], distance=75)
                        r_ICs, _ = find_peaks(-heel_data_r[offset:, 2], distance=75)
                        # plt.plot(-heel_data_l[offset:, 2])
                        # plt.plot(peakList, -heel_data_l[peakList + offset, 2], 'x')
                        # plt.show()
                        # l_ICs = IC_from_heel(heel_data_l[:, 2])
                        # r_ICs = IC_from_heel(heel_data_r[:, 2])
                        l_ICs += offset
                        r_ICs += offset
                        send_to_json(l_ICs.tolist(), r_ICs.tolist(), trial, subjectDict)
            out_file = open(subject + ".json", "w")
            print(subjectDict)
            json.dump(subjectDict, out_file, indent=4)
            plt.show()


if __name__ == "__main__":
    main()
