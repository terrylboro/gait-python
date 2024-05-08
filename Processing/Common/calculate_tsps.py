# Calculate the temporal-spatial parameters (TSPs) from processed gait data
# Written by Terry Fawden 1/9/2023
import json

import numpy as np
import pandas as pd
from scipy.ndimage import shift  # use this to shift the arrays
import os
import re


def load_events_shank(subject, trial):
    eventsDict = {}
    filepath = "../Shank/Events/Gyro/RawEvents/TF_" + str(subject).zfill(2) + ".json"
    # read json file
    try:
        with open(filepath, 'r') as jsonfile:
            data = json.load(jsonfile)
            json_str = json.dumps(data[str(trial).zfill(4)])
            pd_df = pd.read_json(json_str, orient='index')
            eventsDict = pd_df.T
            return eventsDict
    except:
        print("No events for subject {}".format(subject))


def load_events_earables(subject, trial):
    eventsDict = {}
    filepath = "../Ear/Events/AdaptedDiao/RawEvents/TF_" + str(subject).zfill(2) + ".json"
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    sides = ["left", "right", "chest"]
    for side in sides:
        try:
            json_str = json.dumps(data[str(trial).zfill(4)][side])
            pd_df = pd.read_json(json_str, orient='index')
            eventsDict[side] = pd_df.T
            return eventsDict
        except:
            print("No events for subject {} side {}".format(subject, side))

def load_events_optical(subject, trial):
    eventsDict = {}
    filepath = "../../C3d/OwnGroundTruth/RawEventsWalksAndTurf/TF_" + str(subject).zfill(2) + ".json"
    # filepath = "../../C3d/CombinedData/TF_" + str(subject).zfill(2) + ".json"
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
    try:
        json_str = json.dumps(data[str(trial).zfill(4)])
        pd_df = pd.read_json(json_str, orient='index')
        eventsDict = pd_df.T
        return eventsDict
    except:
        print("No events for subject {}".format(subject))


def calculate_TSPs(RHC, LHC, RTO, LTO, trialNum):
    """
    Calculate all the TSPs from the initial contact and foot off locations
    """
    col_names = ["Trial", "Left Stride Time", "Right Stride Time", "Left Stance Time", "Right Stance Time",
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
    df["Trial"] = pd.Series([trialNum] * len(df))
    # try:
    #     os.mkdir("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/TSPs/"+subject)
    # except OSError as error:
    #     print(error)
    # df.to_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/TSPs/" + subject + "/trial-" + str(trial_num).zfill(2) + "-" + side + "-TSPs.csv")
    # df.to_csv(save_dir, index_label="Index")
    return df
    # print(df)

def calculate_TSPs_one_side(LHC, LTO, trialNum):
    """
        Calculate all the TSPs from the initial contact and foot off locations on shank or wrist
        """
    col_names = ["Trial", "Left Stride Time", "Left Stance Time", "Left Swing Time", "Left Swing/Stance Ratio", "Step Asymmetry"]
    # Create a Dataframe to store all the info
    df = pd.DataFrame(columns=col_names)
    left_stride_time = stride_time(LHC)
    # Line-up and trim the data so calculations work
    LHC = np.trim_zeros(LHC)
    LTO = np.trim_zeros(LTO)
    left_stance_time = stance_time(LHC, LTO)
    left_swing_time = swing_time(LHC, LTO)
    ssr_left = calculate_SSR(left_swing_time, left_stance_time)
    # Populate the dataframe
    df["Left Stride Time"] = pd.Series(left_stride_time)
    df["Left Stance Time"] = pd.Series(left_stance_time)
    df["Left Swing Time"] = pd.Series(left_swing_time)
    df["Left Swing/Stance Ratio"] = pd.Series(ssr_left)
    df["Trial"] = pd.Series([trialNum] * len(df))
    return df


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
    ssrL = np.nanmean(ssrL)
    ssrR = np.nanmean(ssrR)
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


def find_trial_nums(dir):
    trialNums = []
    for file in dir:
        temp = re.findall(r'\d+', file)
        res = list(map(int, temp))
        trialNums.append(res[1])
    return trialNums


def main():
    usingEarables = False
    usingShank = False
    # Try this in a loop
    # for subjectNum in [x for x in range(0, 61) if x not in [20, 22]]:#, 40, 41, 46, 47, 48, 61]]:
    for subjectNum in [x for x in range(56, 68) if x not in [40, 41, 46, 47, 48, 61]]:
        if usingShank:
            colNames = ["Trial", "Left Stride Time", "Left Stance Time", "Left Swing Time", "Left Swing/Stance Ratio", "Step Asymmetry"]
        else:
            colNames = ["Trial", "Left Stride Time", "Right Stride Time", "Left Stance Time", "Right Stance Time",
                                   "Left Swing Time", "Right Swing Time", "Left Swing/Stance Ratio", "Right Swing/Stance Ratio", "Step Asymmetry"]
        tspSummarydf = pd.DataFrame(columns=colNames)

        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum).zfill(2) in goodSubjects:
            # find the trial numbers which correspond to various walking events
            walkTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/Walk/Right/".format(str(subjectNum).zfill(2)))
            walkSlowTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/WalkSlow/Right/".format(str(subjectNum).zfill(2)))
            # walkNodTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/WalkNod/Right/".format(str(subjectNum).zfill(2)))
            # walkShakeTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/WalkShake/Right/".format(str(subjectNum).zfill(2)))
            if subjectNum > 33 and str(subjectNum) not in ["41", "61"]:
                turf2floorTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/Turf2Floor/Right/".format(str(subjectNum).zfill(2)))
                floor2turfTrialFiles = os.listdir("../../TiltCorrectedData/TF_{}/Floor2Turf/Right/".format(str(subjectNum).zfill(2)))
                shoeBoxTrialFiles = os.listdir(
                    "../../TiltCorrectedData/TF_{}/ShoeBox/Right/".format(str(subjectNum).zfill(2)))
                turf2floorTrialNums = find_trial_nums(turf2floorTrialFiles)
                floor2turfTrialNums = find_trial_nums(floor2turfTrialFiles)
                shoeBoxTrialNums = find_trial_nums(shoeBoxTrialFiles)
            # getting numbers from string
            walkTrialNums = find_trial_nums(walkTrialFiles)
            walkSlowTrialNums = find_trial_nums(walkSlowTrialFiles)
            # walkNodTrialNums = find_trial_nums(walkNodTrialFiles)
            # walkShakeTrialNums = find_trial_nums(walkShakeTrialFiles)
            print(walkTrialNums)
            print(subjectNum)
            if usingEarables or usingShank:
                subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
                for file in os.listdir(subjectDir):
                    trialNum = int(file.split(".")[0].split("-")[-1])
                    if trialNum in walkTrialNums:
                        if usingEarables:
                            eventsDict = load_events_earables(subjectNum, trialNum)
                            if eventsDict is not None:
                                print(eventsDict["left"])
                                LHC = eventsDict["left"]['LHC'].values
                                RHC = eventsDict["left"]['RHC'].values
                                LTO = eventsDict["left"]['LFO'].values
                                RTO = eventsDict["left"]['RFO'].values
                                trialTSPs = calculate_TSPs(RHC, LHC, RTO, LTO, trialNum)
                                tspSummarydf = pd.concat([tspSummarydf, trialTSPs], axis=0)
                        else:
                            eventsDict = load_events_shank(subjectNum, trialNum)
                            if eventsDict is not None:
                                LHC = eventsDict["LHC"].values
                                LTO = eventsDict["LFO"].values
                                trialTSPs = calculate_TSPs_one_side(LHC, LTO, trialNum)
                                tspSummarydf = pd.concat([tspSummarydf, trialTSPs], axis=0)
            else:
                subjectDir = "../../C3d/OwnGroundTruth/RawEventsWalksAndTurf/TF_{}.json".format(str(subjectNum).zfill(2))
                # subjectDir = "../../C3d/CombinedData/TF_{}.json".format(str(subjectNum).zfill(2))
                # for file in os.listdir(subjectDir):
                #     if file.endswith(".json"):
                # trialNum = int(file.split(".")[0].split("_")[-1])
                # print(trialNum)
                for trialNum in walkTrialNums:
                    eventsDict = load_events_optical(subjectNum, trialNum)
                    if eventsDict is not None:
                        print(eventsDict)
                        LHC = eventsDict['LHC'].values
                        RHC = eventsDict['RHC'].values
                        LTO = eventsDict['LFO'].values
                        RTO = eventsDict['RFO'].values
                        trialTSPs = calculate_TSPs(RHC, LHC, RTO, LTO, trialNum)
                        tspSummarydf = pd.concat([tspSummarydf, trialTSPs], axis=0)

            tspSummarydf.to_csv(str(subjectNum).zfill(2) + ".csv", index=False)


if __name__ == "__main__":
    main()




