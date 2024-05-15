from scipy import signal, integrate
import pywt
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import json


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

def determine_sides(HC, TO, side, gyroData):
    LHC = []
    RHC = []
    LTO = []
    RTO = []
    left_first = False
    plt.plot(gyroData, 'r')
    gyroData = bp_filter_chest(gyroData, [0.5, 5])
    # plt.figure()
    plt.plot(gyroData)
    # plt.show()
    # right or left depends on polarity of gyro
    for i in range(0, len(gyroData[HC])):
        if gyroData[HC][i] < 0:
            LHC.append(HC[i])
            if i == 0:
                left_first = True
        else:
            RHC.append(HC[i])
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
    # if side == "right":
    #     # Swap R and L to allow for the different sensor co-ordinates systems
    #     return RHC, LHC, RTO, LTO
    # else:
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
    plt.show()
    return ic_peaks, fc_peaks


def main():
    # import the data
    for subjectNum in [x for x in range(22, 23) if x not in [46, 47, 48]]:
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum) + "," in goodSubjects:
            subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
            subjectDict = {}
            for file in os.listdir(subjectDir):
                # load ear data
                trialNum = int(file.split(".")[0].split("-")[-1])
                subjectDict[str(trialNum).zfill(4)] = {"left": {}, "right": {}, "chest": {}}
                print("{}: {}".format(subjectNum, trialNum))
                # if trialNum == 8:
                for side in ["chest"]:
                    data = pd.read_csv(os.path.join(subjectDir, file), usecols=["AccZ" + side, "GyroX" + side])
                    plt.plot(data["AccZ" + side], 'y')
                    # plt.title("{}-{}".format(side, trialNum))
                    # plt.show()
                    ICs, FOs = apply_mccamley(data["AccZ"+side].values, 100, 5, 10)
                    # ICs = remove_outliers(ICs)
                    # FOs = remove_outliers(FOs)
                    LICs_l, RICs_l, LTCs_l, RTCs_l = determine_sides(ICs, FOs, side, data["GyroX"+side].values)
                    print("LICs:\n", LICs_l)
                    print("RICs:\n", RICs_l)
                    send_to_json(LICs_l, RICs_l, LTCs_l, RTCs_l, str(trialNum).zfill(4), side, subjectDict)
            # # dump to subject-specific json file
            # out_file = open("../Chest/Events/McCamley/RawEvents/TF_{}".format(str(subjectNum).zfill(2)) + ".json", "w")
            # json.dump(subjectDict, out_file, indent=4)


if __name__ == "__main__":
    main()
