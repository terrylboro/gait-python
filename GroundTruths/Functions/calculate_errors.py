# Calculate the errors in gait event locations observed from a method versus ground truth
import os

import numpy as np
import pandas as pd


def calculate_errors(est_filepath, gt_filepath, savedir=None):
    # load the data from file and replace any zeros as NaN
    gt_df = pd.read_csv(gt_filepath)
    est_df = pd.read_csv(est_filepath)
    gt_df.replace(0, np.nan, inplace=True)
    est_df.replace(0, np.nan, inplace=True)
    # Find the lengths of each to apply necessary padding and determine correct size of error df
    initial_gt_df_len = len(gt_df)
    initial_est_df_len = len(est_df)
    longest_array = max(initial_est_df_len, initial_gt_df_len)
    diff_in_df_len = abs(initial_est_df_len - initial_gt_df_len) + 1
    if initial_est_df_len > initial_gt_df_len:
        gt_df = gt_df.reindex(range(0, longest_array))
    elif initial_est_df_len < initial_gt_df_len:
        est_df = est_df.reindex(range(0, longest_array))
    # cycle through gait events to determine offsets
    diffs = np.empty((4, initial_est_df_len), dtype=np.float32)
    for i in range(0, initial_est_df_len):
        diffs[0, i] = abs(gt_df.at[0, 'LHC'] - est_df.shift(periods=-i).at[0, 'LHC'])
        diffs[1, i] = abs(gt_df.at[0, 'RHC'] - est_df.shift(periods=-i).at[0, 'RHC'])
        diffs[2, i] = abs(gt_df.at[0, 'LTO'] - est_df.shift(periods=-i).at[0, 'LTO'])
        diffs[3, i] = abs(gt_df.at[0, 'RTO'] - est_df.shift(periods=-i).at[0, 'RTO'])
    min_diffs = np.nanargmin(diffs, axis=1)
    # using these offsets, find the difference between estimate and ground truth
    events_cols = ['LHC', 'RHC', 'LTO', 'RTO']  # the col names as array to allow iteration
    error_cols = ['LHC Error', 'RHC Error', 'LTO Error', 'RTO Error']
    error_array = np.empty_like(est_df.to_numpy())
    for col in range(0, len(error_cols)):
        error_array[:, col] = est_df.shift(periods=-min_diffs[col])[events_cols[col]].to_numpy() - gt_df[events_cols[col]].to_numpy()

    # format these results into a summary dataframe
    error_df = pd.DataFrame(error_array[:, :4], columns=error_cols)
    # loop through to fix back the offsets
    for col in range(0, len(events_cols)):
        error_df[error_cols[col]] = error_df[error_cols[col]].shift(periods=min_diffs[col])
        gt_df[events_cols[col]] = gt_df[events_cols[col]].shift(periods=min_diffs[col])
    # format the original dataframes then concatenate them into a summary
    est_df = est_df.rename(columns={"LHC": "LHC Measured", "RHC": "RHC Measured", "LTO": "LTO Measured", "RTO": "RTO Measured"})
    est_df.drop(columns=['Index', 'Trial'], inplace=True)
    gt_df = gt_df.rename(columns={"LHC": "LHC True", "RHC": "RHC True", "LTO": "LTO True", "RTO": "RTO True"})
    gt_df.drop(columns=['Index', 'Trial'], inplace=True)
    # save_col_names = ['Trial', 'LHC Measured', 'RHC Measured', 'LTO Measured', 'RTO Measured',
    #                   'LHC True', 'RHC True', 'LTO True', 'RTO True',
    #                   'LHC Error', 'RHC Error', 'LTO Error', 'RTO Error']
    summary_df = pd.concat([est_df, gt_df], axis=1)
    summary_df = pd.concat([summary_df, error_df], axis=1)
    print(summary_df)
    # save these to a folder
    if savedir is not None:
        summary_df.to_csv(savedir + est_filepath.split("/")[-1], index=False)




def main():
    subject = "Jamie"
    estdir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Processing/McCamley Wavelet/" + subject + "/"
    gtdir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/" + subject + "/Parsed/"
    savedir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Processing/McCamley Wavelet/" + subject + "/Summary/"
    try:
        os.mkdir(savedir)
    except OSError:
        print("Folder already exists!")
    # loop through all files in the directory
    for file in os.listdir(estdir):
        if file.endswith('.csv'):
            print(file)
            # trial_num = file.split('.')[0][-2:] if file.split('.')[0][-2:].isdigit() else file.split('.')[0][-1:]
            trial_num = file.split('-')[-2][-2:] if len(file.split('-')[-2]) > 1 else file.split('-')[-2][-1:]
            print("Trial num: ", trial_num)
            est_filepath = estdir + file
            gt_filepath = gtdir + "events-" + trial_num.zfill(2) + ".csv"
            if os.path.isfile(gtdir + "events-"+trial_num.zfill(2)+".csv"):
                calculate_errors(est_filepath, gt_filepath, savedir)



if __name__ == "__main__":
    main()





