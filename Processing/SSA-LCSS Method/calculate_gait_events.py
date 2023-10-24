# An implementation of Jarchi's gait event detection algorithm
# https://www.researchgate.net/publication/260836636_Gait_Parameter_Estimation_From_a_Miniaturized_Ear-Worn_Sensor_Using_Singular_Spectrum_Analysis_and_Longest_Common_Subsequence
# Written by Terry Fawden 29/8/2023

from scipy.signal import find_peaks
from ssa import SSA
from lcss_tslearn import perform_lcss
from Processing.Common.calculate_tsps import calculate_TSPs
from Processing.Common.tilt_correct import *
import os
import pandas as pd
from Processing.Common.save_gait_events import save_gait_events
from GroundTruths.Functions.compare_with_ground_truth import compare_with_ground_truth


def calculate_gait_events(data, offset):
    """ Calculate the gait events from inputted accelerometer data\n
    Inputs: AP, SI and ML data from ear-worn IMU\n
    Outputs: Locations of heel contacts and toe-offs """
    # Segment gait signals from acceleration data
    s1 = data[:, 2]  # the ML axis
    s2 = data[:, 0]  # the AP axis
    s3 = data[:, 1]  # the SI axis
    # Detect RHC and LHC
    window = 70  # define the window length for SSA
    plt.figure()
    plt.plot(s3)
    ssa_y = SSA(s3, window)
    plt.figure()
    y = ssa_y.reconstruct([1, 2])
    plt.plot(y)
    plt.show()
    # find local minima and maxima, must be < 0 and > 0 respectively
    i_min, i_min_heights = find_peaks(-y, height=0)
    i_max, i_max_heights = find_peaks(y, height=0)
    print(i_min)
    # Create trend-removed time series for each axis
    s1_tilda = SSA(s1, window).trend_removal()
    s2_tilda = SSA(s2, window).trend_removal()
    s3_tilda = SSA(s3, window).trend_removal()
    tau1 = 1
    h = np.zeros(len(i_min), dtype=np.uint16)
    for n in range(0, len(i_min)):
        if i_min[n] > 5:
            q = s2_tilda[i_min[n] - tau1 : i_min[n] + tau1] * s3_tilda[i_min[n] - tau1 : i_min[n] + tau1]
            h[n] = q.idxmin()
    # Determine left/right heel contacts using ML axis
    # if s1_tilda[h[3] : h[4]].mean() > s1_tilda[h[4] : h[5]].mean():
    if s1_tilda[h[1]: h[2]].mean() > s1_tilda[h[2]: h[3]].mean():
        RHC = h[np.arange(1, len(h), 2)]
        LHC = h[np.arange(2, len(h), 2)]
    else:
        RHC = h[np.arange(2, len(h), 2)]
        LHC = h[np.arange(1, len(h), 2)]
    print("RHC: ", RHC)
    print("LHC: ", LHC)
    # Segment the ML axis data
    q = min(np.diff(RHC[:-1]))
    plt.figure(1)
    Xc = np.zeros((len(RHC)-1, q))
    for i in range(0, len(RHC)-1):
        Xc[i, :] = s1_tilda[RHC[i]:RHC[i] + q]
    # Find the main gait cycle
    for i in range(0, len(RHC)-1):
        plt.plot(range(0, q), Xc[i, :])
    plt.plot(range(0, q), Xc[1, :])
    plt.figure(3)
    s2_tilda.plot()
    s3_tilda.plot()
    # plt.show()
    U, Sigma, VT = np.linalg.svd(Xc)
    # normalise the 1st vector to give main gait cycle
    plt.figure(2)
    gc = VT.T[:, 0] / np.linalg.norm(VT.T[:, 0])
    # v and -v are valid answers for same lambda
    # so if -v is chosen we can correct it
    if np.sum(np.gradient(gc[:15])) < 0:
        gc = - gc
    # plt.plot(range(0, gc.size), gc)

    # Apply LCSS to find similarity
    RTO = []
    LTO = []
    tau2 = 0.6
    # print(gc)
    for i in range(0, len(Xc)):
        a = (gc - np.mean(gc)) / np.std(gc)
        b = (Xc[i, :] - np.mean(Xc[i, :])) / np.std(Xc[i, :])
        epsilon = 0.3*min(np.std(a), np.std(b))
        delta = np.round(0.15 * min(len(gc), len(Xc[i, :]))).astype(np.int32)
        # similarity, matched_out = lcsMatching(a, b, delta, epsilon)
        similarity, matched_out = perform_lcss(a, b, delta, epsilon, i+5)
        print(similarity)
        # Only find toe-offs if the raw cycle is similar enough to the gc
        if similarity > tau2:
            # Find the RTO: first local min of gc after min LHC(i+j)
            if RHC[0] > LHC[0]:
                loc_RTO = np.argmin(gc[LHC[i+1]-RHC[i]:]) + LHC[i + 1] - RHC[i]
            else:
                loc_RTO = np.argmin(gc[LHC[i] - RHC[i]:]) + LHC[i] - RHC[i]
            # Must handle case if the raw cycle doesn't include a mapping to the local min of gc
            closest_value = sorted(matched_out, key=lambda x: abs(loc_RTO - x[0]))[0]
            RTO.append(closest_value[1] + RHC[i])
            # Find the LTO: first local max of gc before gi = max(LHC(i+j)) for j=0,...,N-1
            # Firstly, make the template
            a1 = 10
            a2 = 10
            b1 = 40
            b2 = 120
            z1 = 600
            z2 = 600
            time = range(0, 75)
            r = np.zeros(len(time))
            # Correct for the error in the paper - exponent should be negative
            for t in time:
                r[t] = a1 * np.exp(- (2*t - b1)**2 / z1) + a2 * np.exp(- (2*t - b2)**2 / z2)
            r = (r - np.mean(r)) / np.std(r)
            # # Find gi (for us this is simply the LHC as we only group in single cycles)
            if RHC[0] > LHC[0]:
                gi = LHC[i+1] - RHC[i]
            else:
                gi = LHC[i] - RHC[i]
            _, r_matched_out = perform_lcss(r, a[0:gi], delta, epsilon, i + 10)
            r_local_max = np.argmax(r_matched_out)
            gc_closest_value = sorted(r_matched_out, key=lambda x: abs(r_local_max - x[0]))[0][1]
            # # we need to find the corresponding point on the raw cycle cj by reusing LCSS(gc,cj)
            cj_closest_value = sorted(matched_out, key=lambda x: abs(gc_closest_value - x[0]))[0][1]
            LTO.append(cj_closest_value + RHC[i])
    # Now calculate the TSPs
    plt.show()
    # correct for cropping
    # LHC += offset
    # RHC += offset
    # LTO += offset
    # RTO += offset
    print("RHC: ", RHC)
    print("LHC: ", LHC)
    print("RTO: ", RTO)
    print("LTO: ", LTO)
    return LHC, RHC, LTO, RTO
    # plt.show()


def main():
    subject = "Jamie"
    filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/CroppedWalk/"
    static_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Static/" + subject + "-static.txt"
    og_data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Walk/"
    savedir_TSP = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/TSPs/" + subject + "/SSALCSS/"
    try:
        os.mkdir(savedir_TSP)
    except OSError:
        print("Directory already exists!")
    try:
        os.mkdir(os.getcwd() + "/" + subject + "/")
    except OSError:
        print("Directory already exists!")


    # Firstly, calculate the calibration rotation matrix
    # calib_data = np.loadtxt(static_filepath, delimiter=',', usecols=[2, 3, 4])
    # rot_mat_lear = calculate_rotation_matrix(np.loadtxt(static_filepath, delimiter=',', usecols=[2, 3, 4]))
    # rot_mat_rear = calculate_rotation_matrix(np.loadtxt(static_filepath, delimiter=',', usecols=[11, 12, 13]))

    # cycle through the (cropped) walking files and calculate gait events
    for file in os.listdir(filepath):
        print(file)
        if "jamie-6" in file:
            trial_num = file.split('.')[0][-2:] if file.split('.')[0][-2:].isdigit() else file.split('.')[0][-1:]
            df = pd.read_csv(filepath+file, delimiter=',')
            data_l = df.loc[:, ['AccXlear', 'AccYlear', 'AccZlear']].values
            # data_l = apply_calibration(rot_mat_lear, data_l)
            LHC_lear, RHC_lear, LTO_lear, RTO_lear = calculate_gait_events(data_l, offset=df.at[0, 'Index'])
            save_gait_events(LHC_lear, RHC_lear, LTO_lear, RTO_lear, 'SSA-LCSS Method', subject, trial_num, "left")
            calculate_TSPs(RHC_lear, LHC_lear, RTO_lear, LTO_lear, savedir_TSP + file.split(sep='.')[0] + "-left-TSPs.csv")
            # right side
            data_r = df.loc[:, ['AccXrear', 'AccYrear', 'AccZrear']].values
            # data_r = apply_calibration(rot_mat_lear, data_r)
            LHC_rear, RHC_rear, LTO_rear, RTO_rear = calculate_gait_events(data_r, offset=df.at[0, 'Index'])
            save_gait_events(LHC_rear, RHC_rear, LTO_rear, RTO_rear, 'SSA-LCSS Method', subject, trial_num, "right")
            calculate_TSPs(RHC_rear, LHC_rear, RTO_rear, LTO_rear, savedir_TSP + file.split(sep='.')[0] + "-right-TSPs.csv")
            compare_with_ground_truth(og_data_filepath + file, LHC_lear, RHC_lear, LTO_lear, RTO_lear, save=False, chest=False)





    # for i in range(4, 10):
    #     filename = "iwan-"+str(i)+".txt"
    #     data = np.loadtxt(filepath+filename, delimiter=',', usecols=[2, 3, 4])
    #     data = apply_calibration(rot_mat, data)
    #     calculate_gait_events(data, filename)


if __name__ == '__main__':
    main()