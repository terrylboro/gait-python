# This function compares the gait events calculated from x method to the ground truth
# And plots both against the raw data
# Written by Terry Fawden 7/9/2023

import numpy as np
import pandas as pd
from GroundTruths.Functions.load_ground_truth import load_ground_truth
from Visualisation.Functions.plot_gait_data import plot_gait_data
import matplotlib.pyplot as plt
import os


def compare_with_ground_truth(subject, trial_num, LHC, RHC, LTO=None, RTO=None, save=False):
    data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Walk/"
    # cols = [2, 3, 4] if side == "right" else [11, 12, 13]
    cols = [2, 3, 4, 11, 12, 13]
    colNames = ['AccXlear', 'AccYlear', 'AccZlear', 'AccXrear', 'AccYrear', 'AccZrear']
    # Load the ground truth arrays
    try:
        LHC_gt, RHC_gt, LTO_gt, RTO_gt = load_ground_truth(subject, trial_num)
    except FileNotFoundError as error:
        print("No ground truth data for trial: ", trial_num)
        return

    # Load and plot the underlying gait signal for context
    # data = np.loadtxt(data_filepath + subject.lower() + '-' + str(int(trial_num)) + ".txt", delimiter=',', usecols=cols)
    data = pd.read_csv(data_filepath + subject.lower() + '-' + str(int(trial_num)) + ".txt", delimiter=',', usecols=cols, names=colNames)
    # plot_gait_data(data, "Gait Event Comparison " + subject + '-' + str(int(trial_num)) + '-' + side, plot_legend=False)
    plot_gait_data(data, "Gait Event Comparison " + subject + '-' + str(int(trial_num)), plot_legend=False)
    # Plot ground truths in bold
    for fig_num in [1, 2]:
        plt.figure(fig_num)
        plt.vlines(LHC_gt, data.to_numpy().min(), data.to_numpy().max(), color='r')
        plt.vlines(RHC_gt, data.to_numpy().min(), data.to_numpy().max(), color='g')
        # Plot calculated events transparently
        plt.vlines(LHC, data.to_numpy().min(), data.to_numpy().max(), color='r', alpha=0.5)#, linestyles='-.')
        plt.vlines(RHC, data.to_numpy().min(), data.to_numpy().max(), color='g', alpha=0.5)#, linestyles='-.')
        # Do the same with Toe-Offs if info provided
        if LTO is not None and RTO is not None:
            plt.vlines(LTO_gt, data.to_numpy().min(), data.to_numpy().max(), color='r', linestyles='--')
            plt.vlines(RTO_gt, data.to_numpy().min(), data.to_numpy().max(), color='g', linestyles='--')
            plt.vlines(LTO, data.to_numpy().min(), data.to_numpy().max(), color='r', linestyles=':', alpha=0.5)
            plt.vlines(RTO, data.to_numpy().min(), data.to_numpy().max(), color='g', linestyles=':', alpha=0.5)

        ax = plt.gca()
        if LTO is not None and RTO is not None:
            ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral',
                       'LHC_gt', 'RHC_gt', 'LHC', 'RHC',
                       'LTO_gt', 'RTO_gt', 'LTO', 'RTO'],
                      loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fancybox=True, shadow=True, ncol=4, fontsize=8)
        else:
            ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral',
                       'LHC_gt', 'RHC_gt', 'LHC_est', 'RHC_est'],
                      loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fancybox=True, shadow=True, ncol=4)
    if save:
        save_filepath = os.getcwd()+"/"+subject+"/"
        try:
            os.mkdir(save_filepath)
        except OSError as error:
            print(error)
            print("Filepath already exists! Will overwrite file.")
        plt.figure(1)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-left-result" + ".png", format="png")
        plt.figure(2)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-right-result" + ".png", format="png")
        plt.show()
        plt.close()

    else:
        plt.show()



