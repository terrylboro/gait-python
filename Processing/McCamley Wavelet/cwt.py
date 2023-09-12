# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6720436/

import numpy as np
from scipy import signal, integrate
import pywt
import matplotlib.pyplot as plt
from GroundTruths.Functions.compare_with_ground_truth import compare_with_ground_truth
from Processing.Common.calculate_tsps import calculate_TSPs
import os


def cwt_algo(data, angV, side, view_plots=False):
    """
    Apply the CWT algorithm as described here:\n
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6720436/
    :param data: 1-axis of data (let's say SI, paper uses AP)
    :return: Gait events (HS, TO)
    """
    # The preprocessing steps
    data = preprocess(data)
    # smax = (fc x Fs) / f
    # where fc=central wavelet freq., Fs sampling freq., f gait freq.
    # f is approx 0.5Hz with av.g speed of 1.5m/s
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5087422/
    # https://pdf.sciencedirectassets.com/271166/1-s2.0-S0966636212X00079/1-s2.0-S0966636212000707/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIL%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCICG1immsgoKthqH48CJmxF7yIYbfDN3%2BZfu12aKub0njAiEAvGbL0Ec8Q5ioug%2B7kNqZJuxfIrVEZHQXdY1Unbzdy%2BwqswUIWhAFGgwwNTkwMDM1NDY4NjUiDJ8A0lW9eOrv6H8S8yqQBYoIUYacDPRRbc7QnrJPUF5sPKs8dRXyZsrGBgqtN8zQ9vVB44CAcUwooQgcsEWVvMnarstJfHbxcN4It2XdrYtL64GxfsDcYfMXvCvk%2BvHe6DpaxMF7mwcLeCRohBwsLfY9TIIxXzwGBBCnxleDs9rmA9qrJdcHX%2Fe4Dd5a6%2F7cuH%2B1mnGUJ5k%2Bz9eK%2BxEdZhkCs4a1uF5Fuaa9EjXEyRAABYqkt7NorrzUmFT2mj8GvK8Q0zWWxmChv9ijBZ7FDgLbIHq64eaLDvIOdt5miDrHAIIGRnT5YaQanZ4kC5%2F76XQP%2FTSQlnOdD94OLc0%2Bb29Kder3sTeeIScR6%2BmOCKcRuC5s4WQh%2B%2FIFlF70sX7XsfgNA9JQf%2Fig398AfrEtzKqzuY6XNmUaR5YfAfRTrxOj1PjehIrkzHdVVqhzOqivTH0DNR1q80ne8EutY6hdQmhhE4sZT8oV3dGPkNu56Gu2hh369V%2BPVTLd8RX0Yaq7cgFAflT7kHE5XcvdqGbZJeVFpD2oUHgxKqw56ggBQ9k%2FSe%2BkJjYue4R5YzE87aRU3RE3301dnmEQkRJ7b6J82%2FfFyZk55HqTOgcjmZd3xoojPMmg7Cp8NFrisHC02uk7WVktCGRD6tcLHYc7Rm8FJWysQ7GOpEryJGpS2cevG5ePc6pfWY99fD0em%2FPNpJPjNu95aEua5W6qc3o1t37DIMxnJE8RjTuIxq2f%2BREcQQlFodhm2Ey0N9ll1NPJ8qH2Me6MRQbqCJKGkJ6WmmOjViZ26ySLKzngdleG5avpoxt%2B90QVo3ZRg1hO2BrB3s1IY%2Bn%2BnXrS5HFn9lMdv7eoJ4M4PvRJ8Q03UdCCYwwOzdLKwtRuXfUvz9qNvsEzGhZSMPvh26cGOrEBw%2FWPfqXnqtJdL88AD0H65dvnoqKOuuMlA4wynHos9Hiteytf9LWXXOjm9KMtRMkuqmdtQkNozbj02hHvCOptMIwV5lPg4T32Yc%2BhIynKVLjt%2FKDWPCBHXhXhNpvYr5Oej5DeB8RAgprtqXtXQwXZQ3uoj%2F1kpkmzQtK7nYCwcwgTJHQ6nDDrk5Yk2hEmk8YVXUCISQrSyW9h5pexXTPizr%2FTloC%2FwmulkaYG%2BjJ1bJg3&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230905T094420Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYYD6U3CWK%2F20230905%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=90ad6bdd197febd2e4d263691850a54ba6436445f056c3c1ab81fad3854bc983&hash=acbe01a4cde7dd512489d74eace8fe5cc5efb2e6fa9339c0c43e177491fc12f9&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0966636212000707&tid=spdf-697f933b-8586-4133-863a-7bba39a80125&sid=b9c9619188ea184710092292fcfacaa2cd37gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1c0f5853550a5f56525e5b&rr=801d88799b204e10&cc=fi
    scale = [1, 16]
    coef, _ = pywt.cwt(data, scale, 'gaus2')
    diff_sig = coef[1]
    # The minima of the differentiated signal (i.e. coeffs[0]) are the HC
    HC, _ = signal.find_peaks(-coef[1], prominence=1.5)
    if view_plots:
        plt.figure()
        plt.imshow(coef, extent=[1, len(data), 1, 16], cmap='PRGn', aspect='auto',
            vmax=abs(coef).max(), vmin=-abs(coef).max())  # doctest: +SKIP
        plt.figure()
        plt.plot(coef[1])
        plt.plot(HC, diff_sig[HC],  'o')
    # # Find the TO/FC locations by differentiating again and finding maxima
    jerk_coef, _ = pywt.cwt(diff_sig, scale, 'gaus1')
    jerk_sig = jerk_coef[1]
    TO, _ = signal.find_peaks(-jerk_sig)
    TO = np.squeeze(TO).tolist()
    if view_plots:
        plt.figure()
        plt.plot(jerk_sig)
        plt.plot(TO, jerk_sig[TO], 'o')
        plt.show()  # doctest: +SKIP

    # Determine left or right contact side
    return determine_sides(HC, TO, side, angV)


def determine_sides(HC, TO, side, gyroData):
    LHC = []
    RHC = []
    LTO = []
    RTO = []
    left_first = False
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
    print("LHC: ", LHC)
    print("RHC: ", RHC)
    print("LTO: ", LTO)
    print("RTO: ", RTO)
    if side == "right":
        # Swap R and L to allow for the different sensor co-ordinates systems
        return RHC, LHC, RTO, LTO
    else:
        return LHC, RHC, LTO, RTO


def preprocess(data):
    """
    Apply the preprocessing steps
    :param data:
    :return: Preprocessed data
    """
    # plt.figure()
    # plt.plot(data)
    data = signal.detrend(data)
    sos = signal.butter(2, 10, 'lp', fs=100, output='sos')
    filtered_data = signal.sosfilt(sos, data)
    processed_data = integrate.cumulative_trapezoid(filtered_data)
    return processed_data


def test_cwt():
    t = np.linspace(-1, 1, 200, endpoint=False)
    sig = np.cos(2 * np.pi * 7 * t) + np.real(np.exp(-7 * (t - 0.4) ** 2) * np.exp(1j * 2 * np.pi * 2 * (t - 0.4)))
    widths = np.arange(1, 31)
    cwtmatr, freqs = pywt.cwt(sig, widths, 'mexh')
    plt.imshow(cwtmatr, extent=[-1, 1, 1, 31], cmap='PRGn', aspect='auto',
    vmax = abs(cwtmatr).max(), vmin = -abs(cwtmatr).max())  # doctest: +SKIP
    plt.show()  # doctest: +SKIP


def main():
    # test_cwt()
    subject = "Amy"
    filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/"+subject+"/"+"Walk/"
    # loop through all files in the directory
    # num_trials = len([entry for entry in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, entry))])
    for file in os.listdir(filepath):
        if file != "tom-2_cropped.txt":
            data_L = np.loadtxt(filepath+file, delimiter=',', usecols=3)
            data_L_angV = np.loadtxt(filepath+file, delimiter=',', usecols=5)
            LHC, RHC, LTO, RTO = cwt_algo(data_L, data_L_angV, side="left", view_plots=False)
            trial_num = file.split(sep='.')[0][-1]
            if int(trial_num) == 0:
                trial_num = file.split(sep='.')[0][-2:]
            print(trial_num)
            compare_with_ground_truth(subject, trial_num, LHC, RHC, LTO, RTO, save=True)
            calculate_TSPs(RHC, LHC, RTO, LTO, subject, trial_num, "left")
            # Repeat for the right side
            data_R = np.loadtxt(filepath+file, delimiter=',', usecols=12)
            data_R_angV = np.loadtxt(filepath+file, delimiter=',', usecols=14)
            LHC, RHC, LTO, RTO = cwt_algo(data_R, data_R_angV, side="right")
            # compare_with_ground_truth(subject, trial_num, "right", LHC, RHC, LTO, RTO, save=False)
            calculate_TSPs(RHC, LHC, RTO, LTO, subject, trial_num, "right")
            # filename = subject.lower()+"-"+str(i)+".txt"
            # Do the left side
            # data_L = np.loadtxt(filepath + filename, delimiter=',', usecols=3)
            # data_L_angV = np.loadtxt(filepath + filename, delimiter=',', usecols=5)
            # LHC, RHC, LTO, RTO = cwt_algo(data_L, data_L_angV, side="left", view_plots=True)
            # compare_with_ground_truth(subject, i, "left", LHC, RHC, LTO, RTO, save=False)
            # calculate_TSPs(RHC, LHC, RTO, LTO, subject, i, "left")
            # # Repeat for the right side
            # data_R = np.loadtxt(filepath + filename, delimiter=',', usecols=12)
            # data_R_angV = np.loadtxt(filepath + filename, delimiter=',', usecols=14)
            # LHC, RHC, LTO, RTO = cwt_algo(data_R, data_R_angV, side="right")
            # compare_with_ground_truth(subject, i, "right", LHC, RHC, LTO, RTO, save=False)
            # calculate_TSPs(RHC, LHC, RTO, LTO, subject, i, "right")


if __name__ == "__main__":
    main()