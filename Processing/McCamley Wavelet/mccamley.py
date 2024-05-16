from scipy import signal, integrate
import pywt
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import json
from Processing.Common.sanity_check import sanity_check


def lp_filter_chest(data, freq):
    b, a = signal.butter(4, freq, btype="low", fs=100, output='ba')
    return signal.filtfilt(b, a, data, axis=0)

def bp_filter_chest(data, freq):
    b, a = signal.butter(1, freq, btype="bp", fs=100, output='ba')
    return signal.filtfilt(b, a, data, axis=0)


def send_to_json(LHC, RHC, LFO, RFO, trial, side, subjectDict):
    if side == "lear":
        location = "left"
    elif side == "rear":
        location = "right"
    else:
        location = "chest"
    subjectDict[trial][location] = {
        "LHC": list(map(int, LHC)),
        "RHC": list(map(int, RHC)),
        "LFO": list(map(int, LFO)),
        "RFO": list(map(int, RFO))
    }


def remove_outliers(events_l):
    blacklist = []
    for event in range(1, len(events_l)):
        if events_l[event] - events_l[event-1] < 45:
            # decide which to remove
            blacklist.append(event-1)
    events_l = np.delete(events_l, blacklist, None)
    return events_l

def stance_time_check(HC, TO):
    # Lineup HC and TO by iteratively shifting to left
    offset = 0
    for i in range(0, len(TO)):
        if TO[i] > HC[0]:
            offset = i
            break
    realigned_TO = TO[offset:]
    return np.subtract(realigned_TO[:len(HC)], HC[:len(realigned_TO)])


def determine_sides(HC, TO, side, gyroData):
    LHC = []
    RHC = []
    LTO = []
    RTO = []
    left_first = False
    plt.plot(gyroData, 'r')
    gyroData = bp_filter_chest(gyroData, [0.5, 25])
    # plt.figure()
    plt.plot(gyroData)
    # attempt sides method using just positions of TO
    # for TO_event in TO:
    #     diffR = np.absolute(HC - TO_event).argmin()
    #     if diffR
    # plt.show()
    # right or left depends on polarity of gyro
    # for i in range(0, len(gyroData[HC])):
    #     if gyroData[HC][i] < 0:
    #         LHC.append(HC[i])
    #         if i == 0:
    #             left_first = True
    #     else:
    #         RHC.append(HC[i])
    if gyroData[HC][0] < 0:
        LHC.extend(HC[0::2])
        RHC.extend(HC[1::2])
        left_first = True
    else:
        LHC.extend(HC[1::2])
        RHC.extend(HC[2::2])
    # Determine RTO/LTO from RHC/LHC
    if left_first:
        if TO[0] < LHC[0]:
            LTO.extend(TO[0::2])
            RTO.extend(TO[1::2])
        else:
            RTO.extend(TO[0::2])
            LTO.extend(TO[1::2])
    else:
        if TO[0] < RHC[0]:
            RTO.extend(TO[0::2])
            LTO.extend(TO[1::2])
        else:
            LTO.extend(TO[0::2])
            RTO.extend(TO[1::2])
    print(np.mean(stance_time_check(LHC, LTO)))
    if np.mean(stance_time_check(LHC, LTO) < 50):
        print("Stance time too small - flipping LHC and RHC")
        return RHC, LHC, LTO, RTO
    else:
        return LHC, RHC, LTO, RTO


def apply_mccamley(y_accel, sample_rate, ic_prom, fc_prom):
    # CWT wavelet scale parameters
    scale_cwt1 = [1, 16] #float(sample_rate) / 5.0
    scale_cwt2 = float(sample_rate) / 6.0

    y_accel = bp_filter_chest(y_accel, [0.5, 3])

    # Detrend data
    y_accel -= np.mean(y_accel).flatten()
    detrended_data = signal.detrend(y_accel)
    # print(detrended_data)

    # Low pass filter if less than 40 hz
    filtered_data = detrended_data.flatten() #filter_chest(detrended_data, sample_rate)
    # filtered_data -= np.mean(filtered_data)
    # print(filtered_data[40:50])

    # plt.plot(filtered_data, color='b')

    # cumulative trapezoidal integration
    integrated_data = integrate.cumulative_trapezoid(filtered_data, x=np.linspace(0, (len(filtered_data)-1)/1, len(filtered_data)))
    # print(integrated_data)

    # Gaussian continuous wavelet transform
    cwt_1, freqs = pywt.cwt(y_accel.flatten(), scale_cwt1, 'gaus1')
    differentiated_data = cwt_1[0]
    # plt.plot(differentiated_data[:-2], color="r")

    # initial contact (heel strike) peak detection
    # ic_peaks = signal.find_peaks(pd.Series(-differentiated_data), ic_prom)

    # Gaussian continuous wavelet transform
    cwt_2, freqs = pywt.cwt(-differentiated_data, scale_cwt2, 'gaus1')
    re_differentiated_data = cwt_2[0]
    plt.plot(re_differentiated_data, color="g")
    ic_peaks = signal.argrelmax(re_differentiated_data)[0]
    ic_peaks = ic_peaks[re_differentiated_data[ic_peaks] > 0]

    cwt_3, freqs = pywt.cwt(-re_differentiated_data, scale_cwt2, 'gaus1')
    re_re_differentiated_data = cwt_3[0]
    plt.plot(re_re_differentiated_data, color="k")

    # final contact (toe off) peak detection
    # fc_peaks = signal.find_peaks(pd.Series(re_differentiated_data), fc_prom)
    fc_peaks = signal.argrelmin(re_re_differentiated_data)[0]
    ic_peaks = remove_outliers(ic_peaks)
    fc_peaks = remove_outliers(fc_peaks)
    plt.plot(ic_peaks, re_differentiated_data[ic_peaks], 'bx')
    plt.plot(fc_peaks, re_re_differentiated_data[fc_peaks], 'yx')
    # plt.show()
    return ic_peaks, fc_peaks


def main():
    # import the data
    for subjectNum in [x for x in range(31, 32) if x not in [20, 22, 46, 47, 48]]:
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum) + "," in goodSubjects:
            subjectDir = "../../AlignedZeroedData/TF_{}".format(str(subjectNum).zfill(2))
            subjectDict = {}
            for file in os.listdir(subjectDir):
                print(file)
                # load ear data
                trialNum = int(file.split(".")[0].split("-")[-1])
                subjectDict[str(trialNum).zfill(4)] = {"left": {}, "right": {}, "chest": {}}
                print("{}: {}".format(subjectNum, trialNum))
                for side in ["chest"]:
                    data = pd.read_csv(os.path.join(subjectDir, file), usecols=["AccZ" + side, "GyroZ" + side])
                    firstNonZeroIdx = data.ne(0).idxmax()[0]
                    data = data.iloc[firstNonZeroIdx:, :]
                    plt.plot(data["AccZ" + side], 'y')
                    # plt.title("{}-{}".format(side, trialNum))
                    # plt.show()
                    ICs, FOs = apply_mccamley(data["AccZ"+side].values, 100, 5, 10)
                    eventsDF = sanity_check(ICs, FOs)
                    print(eventsDF)
                    # ICs = remove_outliers(ICs)
                    # FOs = remove_outliers(FOs)
                    LICs_l, RICs_l, LTCs_l, RTCs_l = determine_sides(ICs, FOs, side, data["GyroZ"+side].values)
                    print("LICs:\n", LICs_l)
                    print("RICs:\n", RICs_l)
                    plt.vlines(LICs_l, -3, 3, 'r')
                    plt.vlines(RICs_l, -3, 3, 'g')
                    plt.vlines(LTCs_l, -3, 3, 'r', linestyle='--')
                    plt.vlines(RTCs_l, -3, 3, 'g', linestyle='--')
                    # add the non-zero offset back on
                    LICs_l += firstNonZeroIdx
                    RICs_l += firstNonZeroIdx
                    LTCs_l += firstNonZeroIdx
                    RTCs_l += firstNonZeroIdx
                    # plt.vlines(LICs_l, -3, 3, 'r')
                    # plt.vlines(RICs_l, -3, 3, 'g')
                    plt.title("{}-{}".format(subjectNum, trialNum))
                    plt.show()
                    send_to_json(LICs_l, RICs_l, LTCs_l, RTCs_l, str(trialNum).zfill(4), side, subjectDict)
            # # dump to subject-specific json file
            # out_file = open("../Chest/Events/McCamley/RawEvents/TF_{}".format(str(subjectNum).zfill(2)) + ".json", "w")
            # json.dump(subjectDict, out_file, indent=4)


if __name__ == "__main__":
    main()
