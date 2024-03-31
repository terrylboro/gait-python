import os

import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import json


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

    fp_1 = np.zeros(((end_fr+1) * 20), dtype=np.float32)
    fp_2 = np.zeros(((end_fr+1) * 20), dtype=np.float32)

    fp_1[start_fr * 20:] = np.asarray(itf.GetAnalogDataEx(2, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    fp_2[start_fr * 20:] = np.asarray(itf.GetAnalogDataEx(8, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    heel_data_l = np.zeros((end_fr+1, 3), dtype=np.float32)
    heel_data_r = np.zeros((end_fr+1, 3), dtype=np.float32)
    for j in range(3):
        try:
            heel_data_l[start_fr:, j] = np.asarray(itf.GetPointDataEx(mkr_LHEE, j, start_fr, end_fr, '1'), dtype=np.float32)
            heel_data_r[start_fr:, j] = np.asarray(itf.GetPointDataEx(mkr_RHEE, j, start_fr, end_fr, '1'), dtype=np.float32)
        except:
            print("No heel data")


    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return heel_data_l, heel_data_r, fp_1, fp_2


def IC_from_fp(fp_data):
    return int(round(np.where(fp_data < -10)[0][0] / 20)-1)

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size // 2:]


def IC_from_heel(heel_data):
    max_peaks = find_peaks(heel_data, prominence=15)[0]
    print(max_peaks)
    ICs = []
    for peak in max_peaks:
        ICs.append(int(np.argmin(heel_data[peak:peak+50]) + peak))
    return ICs


def send_to_json(LHC, RHC, trial, subjectDict):
    subjectDict[trial] = {
        "LHC": LHC,
        "RHC": RHC
    }


def main():
    # filepath = "C:/Users/teri-/Documents/GaitC3Ds/A096391_58/A096391_58_0009.c3d"
    # Create json file for given subject
    subjectPath = "C:/Users/teri-/Documents/GaitC3Ds/"
    for subject in os.listdir(subjectPath)[1:]:
        print(subject)
        if int(subject.split("_")[1]) not in [2, 3, 4, 5, 16, 20]:
        # if int(subject.split("_")[1]) in [10]:
            filepath = subjectPath + subject + "/"
            subjectDict = {}
            for file in os.listdir(filepath):
                if file.endswith(".c3d"):
                    trial = file.split('_')[-1].split(".")[0]
                    print(trial)
                    if int(trial) != 1:
                        heel_data_l, heel_data_r, fp_1, fp_2 = get_heel_trajectory(filepath + file)
                        l_ICs = IC_from_heel(heel_data_l[:, 2])
                        r_ICs = IC_from_heel(heel_data_r[:, 2])
                        send_to_json(l_ICs, r_ICs, trial, subjectDict)
            out_file = open(subject + ".json", "w")
            json.dump(subjectDict, out_file, indent=4)
            # autocorrelation
            # z = autocorr(heel_data_l[:, 2])
            # z2 = autocorr(heel_data_r[:, 2])
            # plt.plot(z / float(z.max()), "r--", label="Left")
            # plt.plot(z2 / float(z.max()), "g--", label="Right")
            # plt.legend()
            # plt.title("Autocorrelation")
            # plt.plot(heel_data_l[:, 2] / float(heel_data_l.max()), label="Left")
            # plt.plot(heel_data_r[:, 2] / float(heel_data_r.max()), label="Right")
            # plt.plot(fp_1[0::20])
            # plt.plot(fp_2[0::20])
            # plt.vlines([r_IC, l_IC], 0, 1)
            # plt.vlines([float(r_ICs), float(l_ICs)], 0, 1)
            # plt.show()


if __name__ == "__main__":
    main()
