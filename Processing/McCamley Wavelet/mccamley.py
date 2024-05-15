from scipy import signal, integrate
import pywt
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

def filter_chest(data, freq):
    b, a = signal.butter(2, freq, btype="low", fs=100, output='ba')
    return signal.filtfilt(b, a, data, axis=0)


def apply_mccamley(y_accel, sample_rate, ic_prom, fc_prom):
    # CWT wavelet scale parameters
    scale_cwt1 = [1, 16] #float(sample_rate) / 5.0
    scale_cwt2 = float(sample_rate) / 6.0

    # Detrend data
    y_accel -= np.mean(y_accel).flatten()
    detrended_data = signal.detrend(y_accel)
    # print(detrended_data)

    # Low pass filter if less than 40 hz
    filtered_data = detrended_data.flatten() #filter_chest(detrended_data, sample_rate)
    print(filtered_data[40:50])
    # filtered_data -= np.mean(filtered_data)
    # print(filtered_data[40:50])

    plt.plot(filtered_data, color='b')

    # cumulative trapezoidal integration
    integrated_data = integrate.cumulative_trapezoid(filtered_data, x=np.linspace(0, (len(filtered_data)-1)/1, len(filtered_data)))
    # print(integrated_data)

    # Gaussian continuous wavelet transform
    cwt_1, freqs = pywt.cwt(y_accel.flatten(), scale_cwt1, 'gaus1')
    differentiated_data = cwt_1[0]
    plt.plot(differentiated_data[:-2], color="r")

    # initial contact (heel strike) peak detection
    ic_peaks = signal.find_peaks(pd.Series(-differentiated_data), ic_prom)

    # Gaussian continuous wavelet transform
    cwt_2, freqs = pywt.cwt(-differentiated_data, scale_cwt2, 'gaus1')
    re_differentiated_data = cwt_2[0]
    plt.plot(re_differentiated_data, color="g")

    cwt_3, freqs = pywt.cwt(-re_differentiated_data, scale_cwt2, 'gaus1')
    re_re_differentiated_data = cwt_3[0]
    plt.plot(re_re_differentiated_data, color="k")

    # final contact (toe off) peak detection
    fc_peaks = signal.find_peaks(pd.Series(re_differentiated_data), fc_prom)

    # plt.vlines(fc_peaks, -3, 3, colors="g", linestyles="dashed")
    # plt.vlines(ic_peaks, -3, 3, colors="r", linestyles="dashed")
    plt.show()
    return ic_peaks, fc_peaks


def main():
    # import the data
    for subjectNum in range(28, 29):
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum) + "," in goodSubjects:
            subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
            subjectDict = {}
            for file in os.listdir(subjectDir)[0:1]:
                # load ear data
                trialNum = int(file.split(".")[0].split("-")[-1])
                subjectDict[str(trialNum).zfill(4)] = {"left": {}, "right": {}, "chest": {}}
                print("{}: {}".format(subjectNum, trialNum))
                for side in ["chest"]:
                    data = pd.read_csv(os.path.join(subjectDir, file), usecols=["AccZ" + side])
                    plt.plot(data)
                    plt.title("{}-{}".format(side, trialNum))
                    # plt.show()
                    ICs, FOs = apply_mccamley(data.values, 100, 5, 10)
                    print("ICs: ", ICs)
                    print("FOs: ", FOs)



if __name__ == "__main__":
    main()
