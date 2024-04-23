# Load the parsed ground truth arrays from their saved CSV files
# Written by Terry Fawden 7/9/2023
import os.path

import pandas as pd
import json


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


def load_ground_truth_json(subject, trial):
    filepath = "../Participants/gait_events_A096391_" + str(subject).zfill(2) + ".json"
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    data = data["A096391_" + str(subject).zfill(2)]
    # parse file
    pd_df = pd.read_json(json.dumps(data["A096391_" + str(subject).zfill(2) + "_" + str(trial).zfill(4)]), orient='index')
    return pd_df

def load_ground_truth_json_new(subject, trial):
    filepath = "../../C3d/OwnGroundTruth/RawEvents/TF_" + str(subject).zfill(2) + ".json"
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    try:
        json_str = json.dumps(data[str(trial).zfill(4)])
    except:
        id = str(subject).zfill(2) + str(trial).zfill(2)
        json_str = json.dumps(data[id])
    pd_df = pd.read_json(json_str, orient='index')
    return pd_df


def main():
    """ Test for the json function """
    subject = 17
    for trial in range(3, 6):
        tsps = load_ground_truth_json_new(subject, trial)
        print(tsps.shape)


if __name__ == "__main__":
    main()
