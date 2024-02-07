# Based on the method described by Romijnders et al. 2021
#
# https://jneuroengrehab.biomedcentral.com/articles/10.1186/s12984-021-00828-0
# https://jneuroengrehab.biomedcentral.com/articles/10.1186/1743-0003-11-152
# https://www.mdpi.com/1424-8220/10/6/5683
# Step 1: Identify time intervals at which no GE can occur
# This is based on angular velocity in sagittal plane (w_z)
# Recorded sagittal plane v is largest in midswing, hence T_sw when w_z > 0.2 * max(w_z)
# If this crosses many times in a fraction of a second, take the first and last
# Also, Minimum T_sw is 100ms and two consecutive T_sw on a given foot > 200ms
# IC identified as instant of minimum ML angular velocity in T_IC before instant of max AP acceleration
# FC identified as instant of minimum AP acceleration in the T_FC (since t is expected to occur at the
# time of a sudden motion of the shank preceding the instant of the last maximum AP acceleration value in T_FC)

import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
from scipy.signal import filtfilt, butter, find_peaks, argrelextrema, decimate

def process_shank_accel(ap_accel):
    AP_peaks, _ = find_peaks(ap_accel, prominence=30)
    print(AP_peaks)
    # pair the DZs with the AP peaks to form the T_IC
    # if AP_peaks[0] < DZs[0]:
    #     T_ICs = list(zip(DZs, AP_peaks[1:]))
    # else:
    #     T_ICs = list(zip(DZs, AP_peaks))
    # print(T_ICs)
    # find the local min
    # for T_IC in T_ICs:
    #     local_min = argrelextrema(w_z.loc[T_IC[0] : T_IC[1] + 1].values, np.less)[0]
    #     ICs.extend(T_IC[0] + local_min)


def process_shank_gyro(w_z):
    swing_phase = w_z[w_z > 1.2].index
    #### If we want to block out the swing phase ####
    # w_z = w_z.loc[~w_z.index.isin(swing_phase)]
    #########
    # Finding the ICs
    ZCs = np.where(np.diff(np.signbit(w_z.values)))[0]
    ZCs += 1
    AZs = []
    DZs = []
    ICs = []
    FCs = []
    print(ZCs)
    for crossing in range(1, len(ZCs)):
        count = 0
        print(ZCs[crossing - 1])
        print(ZCs[crossing])
        print(ZCs[crossing+1])
        for i in range(ZCs[crossing - 1], ZCs[crossing]):
            # print(w_z.loc[ZCs[crossing]])
            if w_z.loc[i] > 1: count +=1
        if count > 5 and (w_z.loc[ZCs[crossing] + 2] - w_z.loc[ZCs[crossing] - 2]) < 0:
            DZs.append(crossing)
        print("DZs: ", DZs)
        wait_time = int(0.5 * len(range(ZCs[crossing - 1], ZCs[crossing])))
        for crossing in DZs:
            if len(w_z) - crossing > 15:
                local_min = argrelextrema(w_z.loc[ZCs[crossing] : ZCs[crossing] + 15].values, np.less)[0]
                print(local_min)
                ICs.append(ZCs[crossing] + local_min[0])
        # Say FC is local min in between IC + wait_time and next
        if crossing != ZCs[-1]:
            FC_min = argrelextrema(w_z.loc[ZCs[crossing] + wait_time: ZCs[crossing]+1].values, np.less)[0]
            print(FC_min)
            FCs.append(ZCs[crossing] + wait_time + FC_min)

    # # Finding the Foot Offs
    # for az in AZs:
    #     if az > 15:
    #         local_min = argrelextrema(w_z.loc[az-15 : az + 1].values, np.less)[0]
    #         FCs.append(az - 15 + local_min[-1])
    # plt.plot(ap_accel)
    # plt.plot(w_z)
    # plt.plot(AZs, w_z[AZs], 'x')
    # plt.plot(DZs, w_z[DZs], 'x')
    # plt.plot(ICs, w_z[ICs], 'o')
    # plt.plot(FCs, w_z[FCs], 'o')
    # plt.show()
    return ICs, FCs


def filter(data):
    b, a = butter(2, 25, btype="lp", fs=2000, output='ba')
    filtered_data = filtfilt(b, a, data, axis=0)
    data = filtered_data
    return data


def main():
    subject = str(1).zfill(2)
    activity = "Walk"
    for trial in range(5, 8):
        data = pd.read_csv("../../WristShankData/TF_"+subject+"/"+activity+"/Shank/TF_"+subject+"-"
                           +str(trial).zfill(2)+"shank.csv", usecols=range(0,6))
        # get rid of leading zeros
        first_real_val = np.nonzero(data.values)[0][0]
        print(first_real_val)
        data = data[first_real_val:]
        # low pass filter to chosen frequency
        data = filter(data.values)
        # apply decimation
        data = pd.DataFrame(decimate(data, 20, axis=0, zero_phase=True))

        gyro_data = data.iloc[:, range(3,6)]
        # the sagittal plane angular velocity signal, w_z
        w_z = -gyro_data.iloc[:, 2]#[:, 2]
        plt.plot(w_z)
        plt.show()
        ap_accel = -data.iloc[:, 1]
        # swing_phase = find_w_z_peaks(w_z)
        ICs, FCs = process_shank_gyro(w_z)
        # swing_phase.to_csv("swingphase.csv")
        plt.plot(w_z)
        plt.plot(ap_accel)
        # plt.legend(['X', 'Y', 'Z'])
        plt.plot(ICs, w_z[ICs], 'o')
        plt.plot(FCs, w_z[FCs], 'o')
        plt.show()


if __name__ == "__main__":
    main()
