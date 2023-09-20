# Calculate the temporal-spatial parameters (TSPs) from processed gait data
# Written by Terry Fawden 1/9/2023

import numpy as np
import pandas as pd
from scipy.ndimage import shift  # use this to shift the arrays
import os


def calculate_TSPs(RHC, LHC, RTO, LTO, save_dir):
    """
    Calculate all the TSPs from the initial contact and foot off locations
    """
    col_names = ["Left Stride Time", "Right Stride Time", "Left Stance Time", "Right Stance Time",
                               "Left Swing Time", "Right Swing Time", "Left Swing/Stance Ratio", "Right Swing/Stance Ratio", "Step Asymmetry"]
    col_len = max(len(RHC), len(LHC)) - 1
    # Create a Dataframe to store all the info
    df = pd.DataFrame(columns=col_names)
    left_stride_time = stride_time(LHC)
    right_stride_time = stride_time(RHC)
    # Line-up and trim the data so calculations work
    LHC = np.trim_zeros(LHC)
    RHC = np.trim_zeros(RHC)
    LTO = np.trim_zeros(LTO)
    RTO = np.trim_zeros(RTO)
    # RHC, LHC, RTO, LTO = align_gait_events(RHC, LHC, RTO, LTO)
    left_stance_time = stance_time(LHC, LTO)
    right_stance_time = stance_time(RHC, RTO)
    left_swing_time = swing_time(LHC, LTO)
    right_swing_time = swing_time(RHC, RTO)
    ssr_left = calculate_SSR(left_swing_time, left_stance_time)
    ssr_right = calculate_SSR(right_swing_time, right_stance_time)
    step_asymmetry = calculate_step_asymmetry(ssr_left, ssr_right)
    # Populate the dataframe
    df["Left Stride Time"] = pd.Series(left_stride_time)
    df["Right Stride Time"] = pd.Series(right_stride_time)
    df["Left Stance Time"] = pd.Series(left_stance_time)
    df["Right Stance Time"] = pd.Series(right_stance_time)
    df["Left Swing Time"] = pd.Series(left_swing_time)
    df["Right Swing Time"] = pd.Series(right_swing_time)
    df["Left Swing/Stance Ratio"] = pd.Series(ssr_left)
    df["Right Swing/Stance Ratio"] = pd.Series(ssr_right)
    df["Step Asymmetry"] = pd.Series(step_asymmetry)
    # try:
    #     os.mkdir("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/TSPs/"+subject)
    # except OSError as error:
    #     print(error)
    # df.to_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/TSPs/" + subject + "/trial-" + str(trial_num).zfill(2) + "-" + side + "-TSPs.csv")
    df.to_csv(save_dir, index_label="Index")


def stride_time(HC):
    return np.diff(HC)


def swing_time(HC, TO):
    # Lineup HC and TO by iteratively shifting to left
    offset = 0
    for i in range(0, len(TO)):
        if HC[i] > TO[0]:
            offset = i
            break
    realigned_HC = HC[offset:]
    return np.subtract(realigned_HC[:len(TO)], TO[:len(realigned_HC)])


def stance_time(HC, TO):
    # Lineup HC and TO by iteratively shifting to left
    offset = 0
    for i in range(0, len(TO)):
        if TO[i] > HC[0]:
            offset = i
            break
    realigned_TO = TO[offset:]
    return np.subtract(realigned_TO[:len(HC)], HC[:len(realigned_TO)])


def calculate_SSR(swing, stance):
    """
    Calculate the swing / stance ratio, an indication of asymmetry
    :param swing:
    :param stance:
    :return: Swing / Stance ratio (SSR)
    """
    # print("swing: ", swing)
    # print("stance: ", stance)
    # print("SSR: ", swing / stance * 100)
    num_steps = min(len(stance), len(swing))
    return swing[:num_steps] / stance[:num_steps] * 100


def calculate_step_asymmetry(ssrL, ssrR):
    """
    Use mean swing and stance times to determine asymmetry with sidedness removed
    https://www.apple.com/healthcare/docs/site/Measuring_Walking_Quality_Through_iPhone_Mobility_Metrics.pdf
    :param ssrL: Left SSR
    :param ssrR: Right SSR
    :return: Step asymmetry measure
    """
    ssrL = np.mean(ssrL)
    ssrR = np.mean(ssrR)
    print(ssrL)
    print(ssrR)
    return max(ssrL, ssrR) / min(ssrL, ssrR)


def align_gait_events(RHC, LHC, RTO, LTO):
    """
    Make sure the gait event arrays line up correctly to calculate TSPs
    :param RHC:
    :param LHC:
    :param RTO:
    :param LTO:
    :return: aligned versions of said arrays
    """
    # First, line-up the toe-offs
    if RTO[0] < LTO[0]:
        LTO = LTO[1:]
    # Then align these with the foot contacts
    while RTO[0] < RHC[0]:
        RHC = RHC[1:]
    for c in range(0, len(LHC)):
        if LTO[0] < LHC[c]:
            LHC = LHC[c:]
            break
    return RHC, LHC, RTO, LTO


def apply_padding(data, col_len):
    return np.pad(data, col_len - len(data))


def main():
    # We can test using the ground truth arrays
    # df = pd.read_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/Jamie/Parsed/events-02.csv")
    # LHC = df['LHC'].values
    # RHC = df['RHC'].values
    # LTO = df['LTO'].values
    # RTO = df['RTO'].values
    # calculate_TSPs(RHC, LHC, RTO, LTO, "events-02")
    # Try this in a loop
    subject = "Jamie"
    filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/GroundTruths/" + subject + "/Parsed/"
    for i in range(2, 8):
        try:
            df = pd.read_csv(filepath + "events-" + str(i).zfill(2) + ".csv")
        except FileNotFoundError as error:
            print("No ground truth data for trial: ", i)
            return
        LHC = df['LHC'].values
        RHC = df['RHC'].values
        LTO = df['LTO'].values
        RTO = df['RTO'].values
        calculate_TSPs(RHC, LHC, RTO, LTO, subject, i, 'truth')


if __name__ == "__main__":
    main()




