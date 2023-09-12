# Load the parsed ground truth arrays from their saved CSV files
# Written by Terry Fawden 7/9/2023
import os.path

import pandas as pd


def load_ground_truth(subject, trial_num):
    trial_num = str(trial_num) # ensure this is a string in case int is passed
    gt_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/"\
                  + subject + "/Parsed/events-" + trial_num.zfill(2) + ".csv"
    gt_data = pd.read_csv(gt_filepath)
    LHC = gt_data[gt_data['LHC'] != 0]['LHC'].values.tolist()
    RHC = gt_data[gt_data['RHC'] != 0]['RHC'].values.tolist()
    LTO = gt_data[gt_data['RTO'] != 0]['LTO'].values.tolist()
    RTO = gt_data[gt_data['RTO'] != 0]['RTO'].values.tolist()
    return LHC, RHC, LTO, RTO

