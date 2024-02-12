import numpy as np
import pandas as pd
from scipy import signal, integrate
import pywt
import matplotlib.pyplot as plt
import os


def view_as_cwt(subjectStart, subjectEnd, activityTypes=["Walk"], saveFig=False):
    # all the subfolders in the "/chestShankData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        for activity in activityTypes:
            # loaddir = "../../NEDData/" + subject + "/" + activity + "/Left/"
            loaddir = "../AccZero/Data/" + subject + "/" + activity + "/Right/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                # acc_data = pd.read_csv(filepath, usecols=['AccX', 'AccY', 'AccZ']).values
                acc_data = pd.read_csv(filepath, usecols=['Time', 'Acc0']).values
                # plot the SI plane
                plt.plot(-acc_data[:, 1] + 30, '-g')
                # Apply the cwt
                scale = np.arange(1, 64)
                # coef, _ = pywt.cwt(acc_data, scale, 'gaus2')
                print(pywt.families())
                cwtmatr, freqs = pywt.cwt(acc_data[:, 1], scale, 'morl')
                print(freqs)
                plt.imshow(cwtmatr, cmap='coolwarm', aspect='auto')  # doctest: +SKIP
                plt.title("Timed Up and Go Trial for Participant: " + subject)
                plt.ylabel("Wavelet Coefficients")
                plt.xlabel("Time / Samples")
                plt.show()  # doctest: +SKIP


def main():
    view_as_cwt(5, 18, ["TUG"])


if __name__ == "__main__":
    main()

