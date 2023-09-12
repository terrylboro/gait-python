# Parse the Vicon files for gait events
# Which we can then store in a table and plot
# and use as ground truth to test algorithms
# Written by Terry Fawden 5/9/2023

import numpy as np
import pandas as pd
import csv
import os


def read_ground_truth_data(file, save_dir=None):
    """
    Parse a given Vicon file for gait events
    :param file:
    :return:
    """
    # data = pd.read_csv(file, sep=',')#on_bad_lines='skip')
    truth_text = []
    write_flag = False
    trial_num = file.split('.')[0][-2:]
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            if any(row):
                if row[0] == "Events":
                    write_flag = True
            if write_flag:
                if not any(row):
                    write_flag = False
                else:
                    truth_text.append(','.join(row))
    print(truth_text)
    # Format the DataFrame to fit our spec
    df = pd.DataFrame(truth_text[3:])
    df = df[0].str.split(',', expand=True)
    df = df[[0, 1, 3, 4]]
    df[0] = trial_num
    df = df.set_axis(range(0, 4), axis=1)
    print(df)
    # Now assign these to LHC, RHC, LTO, RTO arrays to make it easy
    cond_left = (df[1] == 'Left')
    cond_strike = (df[2] == 'Strike')
    LHC = df.loc[cond_left & cond_strike, 3].to_list()
    RHC = df.loc[~cond_left & cond_strike, 3].to_list()
    LTO = df.loc[cond_left & ~cond_strike, 3].to_list()
    RTO = df.loc[~cond_left & ~cond_strike, 3].to_list()
    LHC = [int(eval(i)*100) for i in LHC]
    RHC = [int(eval(i) * 100) for i in RHC]
    LTO = [int(eval(i) * 100) for i in LTO]
    RTO = [int(eval(i) * 100) for i in RTO]
    event_array = np.zeros((max(len(LHC), len(RHC), len(LTO), len(RTO)), 4), dtype=np.int64)
    gait_events = [LHC, RHC, LTO, RTO]
    for i in range(0, 4):
        event_array[:len(gait_events[i]), i] = gait_events[i]
    event_array_df = pd.DataFrame(event_array)
    event_array_df.insert(0, "Trial", trial_num)
    event_array_df.columns = ['Trial', 'LHC', 'RHC', 'LTO', 'RTO']
    print(event_array_df)
    if save_dir is not None:
        event_array_df.to_csv(save_dir+"events-"+trial_num+".csv")
    return event_array_df


def main():
    combined_df = pd.DataFrame()
    subject = "Jamie"
    load_dir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/"+subject+"/Raw/"
    save_dir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/"+subject+"/Parsed/"
    try:
        os.mkdir(load_dir)
        os.mkdir(save_dir)
    except OSError as error:
        print(error)
    for filename in os.listdir(load_dir):
        f = os.path.join(load_dir, filename)
        # checking if it is a file
        if os.path.isfile(f):
            combined_df = pd.concat((combined_df, read_ground_truth_data(f, save_dir)))
    combined_df.to_csv(save_dir+"all-events.csv")


if __name__ == "__main__":
    main()
