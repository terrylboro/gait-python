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
import json

import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
from scipy.signal import filtfilt, butter, find_peaks, argrelextrema, decimate, argrelmin


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
    # swing_phase = w_z[w_z > 1.2].index
    #### If we want to block out the swing phase ####
    # w_z = w_z.loc[~w_z.index.isin(swing_phase)]
    #########
    # Finding the ICs
    # print(np.signbit(w_z))
    print(np.where(np.diff(np.signbit(w_z.flatten()))).values)
    # print(np.where(np.diff(np.signbit(w_z)), 0, 1))
    ZCs = np.where(np.diff(np.signbit(w_z)))[0]
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
            if w_z[i] > 1: count +=1
        if count > 5 and (w_z[ZCs[crossing] + 2] - w_z[ZCs[crossing] - 2]) < 0:
            DZs.append(crossing)
        print("DZs: ", DZs)
        wait_time = int(0.5 * len(range(ZCs[crossing - 1], ZCs[crossing])))
        for crossing in DZs:
            if len(w_z) - crossing > 15:
                local_min = argrelextrema(w_z[ZCs[crossing] : ZCs[crossing] + 15].values, np.less)[0]
                print(local_min)
                ICs.append(ZCs[crossing] + local_min[0])
        # Say FC is local min in between IC + wait_time and next
        if crossing != ZCs[-1]:
            FC_min = argrelextrema(w_z[ZCs[crossing] + wait_time: ZCs[crossing]+1], np.less)[0]
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


def simple_process_shank_gyro(w_z):
    """ Find toe-offs and initial contact events from the z gyro signal """
    # firstly, identify all valid zero crossing points
    zeroCrossings = np.where(np.diff(np.signbit(w_z).flatten()))[0] + 1
    # first find the AZ, next ZC is correct DZ, ignore others after
    AZs, DZs = [], []
    for ZCidx in range(0, len(zeroCrossings)):
        # determine if an AZ or DZ
        # first, find the AZ
        evalSpace = 5 if len(w_z) > zeroCrossings[ZCidx] + 5 else len(w_z) - (zeroCrossings[ZCidx] + 1)
        if len(AZs):
            timeSinceLastAZ = zeroCrossings[ZCidx] - AZs[-1]
        else:
            timeSinceLastAZ = 100
        # print(w_z[zeroCrossings[ZCidx] + i] > 0 for i in range(0, evalSpace))
        if all(w_z[zeroCrossings[ZCidx] + i] > 0 for i in range(0, evalSpace)) \
                and timeSinceLastAZ > 80:
            AZs.append(zeroCrossings[ZCidx])
            if ZCidx < len(zeroCrossings)-1:
                DZs.append(zeroCrossings[ZCidx+1])
    # correct for missing DZ as first ZC
    if zeroCrossings[0] not in AZs and zeroCrossings[0] not in DZs:
        # check if there are 2 local minima next door and it follows just a down
        if len(argrelmin(w_z[zeroCrossings[0]:zeroCrossings[0]+25])[0]) > 1\
                and all(w_z[0:zeroCrossings[0]] > 0):
            DZs.append(zeroCrossings[0])
        # if DZs[0] - zeroCrossings[0] > np.mean(np.concatenate([np.diff(DZs), np.diff(AZs)])):
        #     DZs.append(zeroCrossings[0])
        #     DZs.sort()
    plt.plot(AZs, w_z[AZs], 'bx')
    plt.plot(DZs, w_z[DZs], 'gx')
    # then find ICs / FOs using these ZCs
    ICs, FOs = [], []
    for DZ in DZs:
        if DZ < len(w_z) - 11:
            tMin = argrelmin(w_z[DZ:DZ+15])[0] #find_peaks(-w_z[ZC:ZC+10].flatten())[0] #argrelmin(w_z[ZC:ZC+10])[0]
            if tMin.size:
                ICs.append(int(DZ + tMin[0]))
        else:
            tMin = argrelmin(w_z[DZ:len(w_z)])[0]  # find_peaks(-w_z[ZC:ZC+10].flatten())[0] #argrelmin(w_z[ZC:ZC+10])[0]
            if tMin.size:
                ICs.append(int(DZ + tMin[0]))
    for AZ in AZs:
        # tMin = argrelmin(w_z[AZ-20:AZ])[0]
        if AZ > 20:
            tMin = np.argmin(w_z[AZ - 20:AZ])
            FOs.append(int(AZ - (20-tMin)))
        else:
            localMin = np.argmin(w_z[0:AZ])
            if localMin != 0:
                FOs.append(int(localMin))
    ICs.sort()
    FOs.sort()
    return ICs, FOs
    # # firstly, cut out values greater than zero
    # w_z[w_z>0] = 0


def filter_shank(data):
    b, a = butter(2, 25, btype="lp", fs=100, output='ba')
    filtered_data = filtfilt(b, a, data, axis=0)
    data = filtered_data
    return data


def send_to_json(LHC, LFO, trial, subjectDict):
    subjectDict[trial] = {
        "LHC": list(map(int, LHC)),
        "LFO": list(map(int, LFO))
    }


def main():
    # import the data
    for subjectNum in [x for x in range(10, 67) if x not in [20, 22]]:
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum).zfill(2) in goodSubjects:
            subjectDir = "../../AlignedData/TF_{}/".format(str(subjectNum).zfill(2))
            subjectDict = {}
            print(subjectNum)
            for file in os.listdir(subjectDir):
                # load ear data
                trialNum = int(file.split(".")[0].split("-")[-1])
                data = pd.read_csv(subjectDir+file, usecols=["GyroZShank"])
                if subjectNum > 48 and subjectNum != 54:
                    data = data.apply(lambda x: x*-1)
                # get rid of leading zeros
                try:
                    first_real_val, last_real_val = np.nonzero(data.values)[0][0], np.nonzero(data.values)[0][-1]
                    data = data[first_real_val:last_real_val+1]
                    # low pass filter to chosen frequency
                    data = filter_shank(data.values)
                    ICs, FOs = simple_process_shank_gyro(data)
                    plt.vlines(ICs, -1, 1, 'r')
                    plt.vlines(FOs, -4, 0, 'g')
                    # gyro_data = data.iloc[:, range(3,6)]
                    # the sagittal plane angular velocity signal, w_z
                    # plt.plot(data)
                    # plt.title("Shank Forward Rotation from Gyroscope During Walking")
                    # plt.title("{}-{}".format(subjectNum, trialNum))
                    # plt.xlabel("Time / Samples")
                    # plt.ylabel("Angular Velocity / rad/s")
                    # plt.show()
                    ICs += first_real_val
                    FOs += first_real_val
                    send_to_json(ICs, FOs, str(trialNum).zfill(4), subjectDict)
                except:
                    raise "No non-zero data!"
        out_file = open("TF_{}".format(str(subjectNum).zfill(2)) + ".json", "w")
        json.dump(subjectDict, out_file, indent=4)


if __name__ == "__main__":
    main()
