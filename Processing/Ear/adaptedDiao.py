import json

from pyts.decomposition import SingularSpectrumAnalysis
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, argrelextrema, butter, filtfilt


def detect_ic(acc_si_dominant: np.ndarray, acc_ml_wo_trend: np.ndarray, sample_rate_hz: float) -> (np.ndarray, np.ndarray):
    # find minimum on SI axis with removed trend. Peaks corresponds to IC
    peaks_ic, _ = find_peaks(acc_si_dominant * -1, height=0.2, distance=sample_rate_hz * 0.2)
    # determine ipsilateral and contralateral IC
    sides = np.array(["contralateral" for i in range(peaks_ic.shape[0])])

    sides[(acc_ml_wo_trend[peaks_ic + 1] - acc_ml_wo_trend[peaks_ic]) > 0] = "ipsilateral"
    # flipped compared to Diao, because acc_ml was flipped in previous function
    return peaks_ic, sides


def detect_tc(acc_ml_wo_trend: np.ndarray, ic: np.ndarray, sides: np.ndarray) -> (np.ndarray, np.ndarray):
        mins = argrelextrema(acc_ml_wo_trend, np.less, order=2)[0]  # changes np.greater used to be np.less
        contra = ic[sides == "contralateral"]

        contra = contra[contra < mins[-1]]
        tc_ipsi = [int(mins[mins > x][0]) for x in contra]

        maxs = argrelextrema(acc_ml_wo_trend, np.greater, order=2)[0]  # changes  np.less used to be np.greater

        ipsi = ic[sides == "ipsilateral"]
        ipsi = ipsi[ipsi < maxs[-1]]
        tc_contra = [int(maxs[maxs > x][0]) for x in ipsi]

        tc_ipsi = list(set(tc_ipsi))
        tc_contra = list(set(tc_contra))

        # combine
        toe_off = np.array(tc_ipsi + tc_contra).astype(int)
        toe_off_side = np.array(["ipsilateral" for x in tc_ipsi] + ["contralateral" for x in tc_contra])

        # sort
        toe_off_side = toe_off_side[toe_off.argsort()]
        toe_off = toe_off[toe_off.argsort()]
        return toe_off, toe_off_side


def filter_acc(data, freq):
    b, a = butter(2, freq, btype="low", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)


def send_to_json(LHC, RHC, LFO, RFO, trial, side, subjectDict):
    if side == "lear":
        location = "left"
    elif side == "rear":
        location = "right"
    else:
        location = "chest"
    subjectDict[trial][location] = {
        "LHC": list(map(int, LHC)),
        "RHC": list(map(int, RHC)),
        "LFO": list(map(int, LFO)),
        "RFO": list(map(int, RFO))
    }
    # subjectDict[trial][side] = {
    #     "LHC": LHC,
    #     "RHC": RHC,
    #     "LFO": LFO,
    #     "RFO": RFO
    # }

# setup the SSA object
window_length = 100  # sampling freq in Hz
ssa = SingularSpectrumAnalysis(window_size=int(window_length), groups=[[0], [1], [2], np.arange(3, window_length, 1)])

# import the data
for subjectNum in range(59, 68):
    goodSubjects = open("../../Utils/goodTrials",
                        "r").read()
    if "," + str(subjectNum) + "," in goodSubjects:
        subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
        subjectDict = {}
        for file in os.listdir(subjectDir):
            # load ear data
            trialNum = int(file.split(".")[0].split("-")[-1])
            subjectDict[str(trialNum).zfill(4)] = {"left": {}, "right": {}, "chest": {}}
            print("{}: {}".format(subjectNum, trialNum))
            for side in ["lear", "rear", "chest"]:
                data = pd.read_csv(os.path.join(subjectDir, file), usecols=["AccZ"+side, "AccY"+side])
                acc_si = -1 * filter_acc(data["AccZ"+side].to_numpy(), 5).reshape(1, -1)
                acc_ssa_si = ssa.fit_transform(acc_si)[0]
                acc_ml = filter_acc(data["AccY"+side].to_numpy(), 5).reshape(1, -1) * -1  # changed
                acc_ssa_ml = ssa.fit_transform(acc_ml)[0]

                # find gait events
                ic, ic_sides = detect_ic(acc_ssa_si[1], acc_ssa_ml[1], window_length)
                tc, tc_sides = detect_tc(acc_ssa_ml[1] + acc_ssa_ml[2] + acc_ssa_ml[3], ic, ic_sides)
                # add these to df
                LICs_l, RICs_l, LTCs_l, RTCs_l = [], [], [], []
                # LICs, RICs, LTCs, RTCs = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
                for i in zip(ic, ic_sides):
                    if i[1] == "contralateral":
                        if side == "lear" or side == "chest":
                            RICs_l.append(i[0])
                            # RICs.loc[RICs.shape[0]] = i[0]
                        else:
                            LICs_l.append(i[0])
                            # LICs.loc[LICs.shape[0]] = i[0]
                    else:
                        if side == "lear" or side == "chest":
                            LICs_l.append(i[0])
                            # LICs.loc[LICs.shape[0]] = i[0]
                        else:
                            RICs_l.append(i[0])
                            # RICs.loc[RICs.shape[0]] = i[0]
                for i in zip(tc, tc_sides):
                    if i[1] == "contralateral":
                        if side == "lear" or side == "chest":
                            RTCs_l.append(i[0])
                            # RTCs.loc[RTCs.shape[0]] = i[0]
                        else:
                            LTCs_l.append(i[0])
                            # LTCs.loc[LTCs.shape[0]] = i[0]
                    else:
                        if side == "lear" or side == "chest":
                            LTCs_l.append(i[0])
                            # LTCs.loc[LTCs.shape[0]] = i[0]
                        else:
                            RTCs_l.append(i[0])
                            # RTCs.loc[RTCs.shape[0]] = i[0]
                # compile into np array
                # list_len = max([len(i) for i in [LICs, RICs, LTCs, RTCs]])
                # LICs, RICs, LTCs, RTCs = pd.DataFrame(LICs_l), pd.DataFrame(RICs_l), pd.DataFrame(LTCs_l), pd.DataFrame(RTCs_l)
                # eventsDF = pd.concat([LICs, RICs, LTCs, RTCs], ignore_index=True, axis=1)
                # eventsDF.rename({0: "LICs", 1: "RICs", 2: "LTCs", 3: "RTCs"}, axis='columns', inplace=True)
                # eventsDF = pd.DataFrame(data={"LICs": LICs, "RICs": RICs,
                #                               "LTCs": LTCs, "RTCs": RTCs})
                send_to_json(LICs_l, RICs_l, LTCs_l, RTCs_l, str(trialNum).zfill(4), side, subjectDict)
                # print(eventsDF)
                # eventsDF.to_csv(file, index=False)
                ##################

                # # Show the results for the first time series and its subseries
                # plt.figure(figsize=(16, 6))
                #
                # ax1 = plt.subplot(121)
                # ax1.plot(data["AccZ"+side], 'o-', label='Original')
                # ax1.vlines(ic, 6, 15, color='r', linestyle='--')
                # ax1.vlines(tc, 6, 15, color='g', linestyle='--')
                # ax1.legend(loc='best', fontsize=14)
                #
                # ax2 = plt.subplot(122)
                # # for i in range(len(groups)):
                # for i in range(3):
                #     ax2.plot(acc_ssa_si[i], '--', label='SSA {0}'.format(i + 1))
                # ax2.vlines(ic, -2, 4, color='r', linestyle='--')
                # ax2.vlines(tc, -2, 4, color='g', linestyle='--')
                # ax2.legend(loc='best', fontsize=14)
                #
                # plt.suptitle('Singular Spectrum Analysis', fontsize=20)
                #
                # plt.tight_layout()
                # plt.subplots_adjust(top=0.88)
                # plt.show()
            # dump to subject-specific json file
            out_file = open("TF_{}".format(str(subjectNum).zfill(2)) + ".json", "w")
            json.dump(subjectDict, out_file, indent=4)




