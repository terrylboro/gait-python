# Plot the ground truth gait events against the obtained signals
# Written by Terry Fawden 7/9/2023

import numpy as np
import pandas as pd
import os
from Visualisation.Functions.plot_gait_data import plot_gait_data
from load_ground_truth import load_ground_truth
import matplotlib.pyplot as plt


def plot_ground_truths(subject, side, save=False):
    gt_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/" + subject + "/Parsed"
    data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/"
    save_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject + "/Ground Truth vs Raw/"
    subject = subject.lower()
    assert side == "left" or side == "right", "Side must be \"left\" or \"right\""
    cols = [2, 3, 4] if side == "right" else [11, 12, 13]
    # Firstly, load the ground truth data
    for filename in os.listdir(gt_filepath):
        f = os.path.join(gt_filepath, filename)
        # process file for each trial (i.e. excluding all-events)
        if os.path.isfile(f) and filename[0] == "e":
            trial_num = str(int(filename.split('.')[0][-2:]))
            LHC, RHC, LTO, RTO = load_ground_truth(subject, trial_num)
            data = np.loadtxt(data_filepath+subject+'-'+trial_num+".txt", delimiter=',', usecols=cols)
            plot_gait_data(data, "Ground Truth Gait Events for "+subject+'-'+trial_num+'-'+side, plot_legend=False)
            plt.vlines(LHC, np.min(data), np.max(data), color='r')
            plt.vlines(RHC, np.min(data), np.max(data), color='g')
            plt.vlines(LTO, np.min(data), np.max(data), color='r', linestyles='--')
            plt.vlines(RTO, np.min(data), np.max(data), color='g', linestyles='--')

            ax = plt.gca()
            ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral', 'LHC', 'RHC', 'LTO', 'RTO'],
                      loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fancybox=True, shadow=True, ncol=4)
            plt.show()

            if save:
                try:
                    os.mkdir(save_filepath)
                except OSError as error:
                    print(error)
                    print("Filepath already exists! Will overwrite file.")
                plt.savefig(save_filepath+subject+"-"+trial_num+"-"+side+"-GTvsRaw"+".png", format="png")


def main():
    subject = "Tom"
    plot_ground_truths(subject, 'right')#, save=True)


if __name__ == "__main__":
    main()



