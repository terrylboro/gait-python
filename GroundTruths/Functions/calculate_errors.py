# Calculate the errors in gait event locations observed from a method versus ground truth

import numpy as np
import pandas as pd


def calculate_errors(est_filepath, gt_filepath):
    gt_df = pd.read_csv(gt_filepath)
    est_df = pd.read_csv(est_filepath)
    LHC_diffs = np.empty((len(gt_df), len(est_df) - len(gt_df) + 1))
    est_LHC = est_df['LHC'].to_numpy()
    print(est_LHC.shape)
    gt_LHC = gt_df['LHC'].to_numpy()
    print(gt_LHC)
    est_RHC = est_df['RHC'].to_numpy()
    gt_RHC = gt_df['RHC'].to_numpy()
    est_LTO = est_df['LTO'].to_numpy()
    gt_LTO = gt_df['LTO'].to_numpy()
    est_RTO = est_df['RTO'].to_numpy()
    gt_RTO = gt_df['RTO'].to_numpy()
    for i in range(0, len(est_df) - len(gt_df) + 1):
        LHC_diffs[:, i] = abs(gt_LHC - est_LHC)
        # RHC_diffs.append(abs(gt_df.shift(periods=i).at[0, 'RHC'] - est_df.at[0, 'RHC']))
        # LTO_diffs.append(abs(gt_df.shift(periods=i).at[0, 'LTO'] - est_df.at[0, 'LTO']))
        # RTO_diffs.append(abs(gt_df.shift(periods=i).at[0, 'RTO'] - est_df.at[0, 'RTO']))
        print(LHC_diffs)
    # gt_df = gt_df.shift(periods=diffs.index(max(diffs)))
    # gt_df = gt_df.reindex_like(est_df)
    # result_df = (gt_df - est_df).abs()
    # print(result_df)


def main():
    est_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Processing/McCamley Wavelet/Tom/tom-events-3-right.csv"
    gt_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/Tom/Parsed/events-03.csv"
    calculate_errors(est_filepath, gt_filepath)


if __name__ == "__main__":
    main()





