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
    zeroCrossings = np.where(np.diff(np.signbit(w_z).flatten()))[0]
    plt.plot(zeroCrossings, w_z[zeroCrossings], 'rx')
    crossingGaps = np.diff(zeroCrossings).flatten()
    print(crossingGaps)
    validIndices = crossingGaps > 20
    print(validIndices)
    # using just diffs didn't work !!
    # find the correct DZ
    # then find distance to next peak
    # if this is < 85 then we want to blacklist this
    # iterate to the next peak and again blacklist if the gap is too small
    blacklist = []
    for ZCidx in range(0, len(zeroCrossings)-1):
        # determine if an AZ or DZ
        if w_z[zeroCrossings[ZCidx] + 5] < 0:
            # DZ detected
            print("DZ at: ", ZCidx)
            if zeroCrossings[ZCidx+1] - zeroCrossings[ZCidx] < 40:
                blacklist.append(ZCidx+1)
                if ZCidx + 2 < len(zeroCrossings):
                    print(zeroCrossings[ZCidx+2] - zeroCrossings[ZCidx])
                    if zeroCrossings[ZCidx + 2] - zeroCrossings[ZCidx] < 40:
                        blacklist.append(ZCidx+2)
    print(blacklist)
        # if w_z[zeroCrossings[ZCidx] + evalSpace] > 0:
        #     # this is an AZ
        #     if not (30 < zeroCrossings[ZCidx + 1] - zeroCrossings[ZCidx] < 80):


    # validIndices = np.insert(validIndices, np.where(validIndices)[0][-1], True)
    mask = np.ones(len(zeroCrossings), dtype=bool)
    if len(blacklist):
        mask[np.unique(blacklist)] = False
    # mask = np.insert(validIndices, len(mask), True)
    # print(mask)
    # validIndices = validIndices[mask]
    # print(validIndices)
    # validIndices = np.insert(validIndices, 0, False)
    zeroCrossings = zeroCrossings[mask]
    plt.plot(zeroCrossings, w_z[zeroCrossings], 'x')
    # then find ICs / FOs using these ZCs
    ICs, FOs = [], []
    for ZC in zeroCrossings:
        # determine if an AZ or DZ
        evalSpace = 5 if len(w_z) > ZC + 5 else len(w_z) - (ZC + 1)
        if w_z[ZC+evalSpace] < 0:
            # plt.plot(ZC, w_z[ZC], 'x')
            # this is a DZ
            if len(w_z) - ZC > 10:
                tMin = argrelmin(w_z[ZC:ZC+10])[0] #find_peaks(-w_z[ZC:ZC+10].flatten())[0] #argrelmin(w_z[ZC:ZC+10])[0]
                print(tMin)
                if tMin.size:
                    ICs.append(int(ZC + tMin[0]))
        elif w_z[ZC+evalSpace] > 0:
            # this is an AZ
            if ZC > 20:
                tMin = argrelmin(w_z[ZC-20:ZC])
                if tMin[0].size:
                    FOs.append(int(ZC - (20-tMin[0][0])))
        else:
            # some strange plateau which we should probably discard
            raise "Strange plateau - no gait event detected here"
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
    for subjectNum in range(40, 41):
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum) + "," in goodSubjects:
            subjectDir = "../../AlignedData/TF_{}/".format(str(subjectNum).zfill(2))
            subjectDict = {}
            print(subjectNum)
            for file in os.listdir(subjectDir):
                # load ear data
                trialNum = int(file.split(".")[0].split("-")[-1])
                data = pd.read_csv(subjectDir+file, usecols=["GyroZShank"])
                # get rid of leading zeros
                try:
                    first_real_val, last_real_val = np.nonzero(data.values)[0][0], np.nonzero(data.values)[0][-1]
                    data = data[first_real_val:last_real_val]
                    # low pass filter to chosen frequency
                    data = filter_shank(data.values)
                    ICs, FOs = simple_process_shank_gyro(data)
                    plt.vlines(ICs, -1, 1, 'r')
                    plt.vlines(FOs, -4, 0, 'g')
                    # gyro_data = data.iloc[:, range(3,6)]
                    # the sagittal plane angular velocity signal, w_z
                    plt.plot(data)
                    plt.title("Shank Forward Rotation from Gyroscope During Walking")
                    plt.xlabel("Time / Samples")
                    plt.ylabel("Angular Velocity / rad/s")
                    plt.show()
                    send_to_json(ICs, FOs, str(trialNum).zfill(4), subjectDict)
                except:
                    raise "No non-zero data!"
            out_file = open("TF_{}".format(str(subjectNum).zfill(2)) + ".json", "w")
            json.dump(subjectDict, out_file, indent=4)


if __name__ == "__main__":
    main()
