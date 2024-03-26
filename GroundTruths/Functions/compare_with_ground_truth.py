# This function compares the gait events calculated from x method to the ground truth
# And plots both against the raw data
# Written by Terry Fawden 7/9/2023

import numpy as np
import pandas as pd
from GroundTruths.Functions.load_ground_truth import load_ground_truth, load_ground_truth_json, \
    load_ground_truth_json_new
from Visualisation.Functions.plot_gait_data import plot_gait_data
import matplotlib.pyplot as plt
import os


def compare_with_ground_truth(data_filepath, LHC, RHC, LTO=None, RTO=None, save=False, chest=False):
    # Parse for subject and trial_num
    trial_num = data_filepath.split(sep='.')[0][-2:] if data_filepath.split(sep='.')[0][-2:].isdigit() else data_filepath.split(sep='.')[0][-1]
    subject = data_filepath.split(sep='/')[-3]
    # select columns to compare, depending on which sensors we use
    if not chest:
        colNames = ['AccXlear', 'AccYlear', 'AccZlear', 'AccXrear', 'AccYrear', 'AccZrear']
        cols = [2, 3, 4, 11, 12, 13]
    else:
        colNames = ['AccXlear', 'AccYlear', 'AccZlear', 'AccXrear', 'AccYrear', 'AccZrear', 'AccXchest', 'AccYchest', 'AccZchest']
        cols = [2, 3, 4, 11, 12, 13, 20, 21, 22]
    ground_truth_available = True
    # Load and plot the underlying gait signal for context
    data = pd.read_csv(data_filepath, delimiter=',', usecols=cols, names=colNames)
    # plot_gait_data(data, "Gait Event Comparison " + subject + '-' + str(int(trial_num)), plot_legend=False, chest=chest)
    plot_gait_data(data, "Gait Event Comparison for Subject B", plot_legend=False, chest=chest)
    # Load the ground truth arrays
    try:
        gt_df = load_ground_truth_json_new(subject, trial_num)
        LHC_gt = gt_df.iloc[0, :].values
        RHC_gt = gt_df.iloc[1, :].values
        # LTO_gt = gt_df.iloc[2, :].values
        # RTO_gt = gt_df.iloc[3, :].values
    except FileNotFoundError:
        print("No ground truth data for trial: ", trial_num)
        ground_truth_available = False
    # Plot ground truths in bold
    iters = [1, 2] if not chest else [1, 2, 3]
    for fig_num in iters:
        plt.figure(fig_num)
        if ground_truth_available:
            plt.vlines(LHC_gt, data.to_numpy().min(), data.to_numpy().max(), color='r')
            plt.vlines(RHC_gt, data.to_numpy().min(), data.to_numpy().max(), color='g')
        # Plot calculated events transparently
        plt.vlines(LHC[:, fig_num-1], data.to_numpy().min(), data.to_numpy().max(), color='r', alpha=0.5)#, linestyles='-.')
        plt.vlines(RHC[:, fig_num-1], data.to_numpy().min(), data.to_numpy().max(), color='g', alpha=0.5)#, linestyles='-.')
        # Do the same with Toe-Offs if info provided
        # if LTO is not None and RTO is not None:
        #     if ground_truth_available:
        #         plt.vlines(LTO_gt, data.to_numpy().min(), data.to_numpy().max(), color='r', linestyles='--')
        #         plt.vlines(RTO_gt, data.to_numpy().min(), data.to_numpy().max(), color='g', linestyles='--')
        #     plt.vlines(LTO[:, fig_num-1], data.to_numpy().min(), data.to_numpy().max(), color='r', linestyles=':', alpha=0.5)
        #     plt.vlines(RTO[:, fig_num-1], data.to_numpy().min(), data.to_numpy().max(), color='g', linestyles=':', alpha=0.5)

        ax = plt.gca()
        if ground_truth_available:
            if LTO is not None and RTO is not None:
                ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral',
                           'LHC_gt', 'RHC_gt', 'LHC_est', 'RHC_est',
                           'LTO_gt', 'RTO_gt', 'LTO_est', 'RTO_est'],
                          loc='upper center', bbox_to_anchor=(0.5, -0.15),
                          fancybox=True, shadow=True, ncol=4, fontsize=8)
            else:
                ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral',
                           'LHC_gt', 'RHC_gt', 'LHC_est', 'RHC_est'],
                          loc='upper center', bbox_to_anchor=(0.5, -0.15),
                          fancybox=True, shadow=True, ncol=4)
        else:
            if LTO is not None and RTO is not None:
                ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral',
                           'LHC_est', 'RHC_est', 'LTO_est', 'RTO_est'],
                          loc='upper center', bbox_to_anchor=(0.5, -0.15),
                          fancybox=True, shadow=True, ncol=4, fontsize=8)
            else:
                ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral', 'LHC_est', 'RHC_est'],
                          loc='upper center', bbox_to_anchor=(0.5, -0.15),
                          fancybox=True, shadow=True, ncol=4)
    if save:
        save_filepath = os.getcwd()+"/"+subject+"/"
        try:
            os.mkdir(save_filepath)
        except OSError:
            print("Filepath already exists! Will overwrite file.")
        plt.figure(1)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-left-result" + ".png", format="png", dpi=600)
        plt.figure(2)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-right-result" + ".png", format="png", dpi=600)
        plt.figure(3)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-chest-result" + ".png", format="png", dpi=600)
        # plt.show()
        plt.close()

    else:
        plt.show()



