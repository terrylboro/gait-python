import numpy as np
import pandas as pd
import os
from GroundTruths.Functions.load_ground_truth import load_ground_truth
import matplotlib.pyplot as plt

def plot_left_cycles(data, LHC, offset, trial_num):
    # firstly, segment the data into gait cycles using the foot contact points
    l_mod = [0] + LHC + [max(LHC) + 1]
    list_of_l = [data.iloc[l_mod[n]+offset:l_mod[n + 1]+offset] for n in range(len(l_mod) - 1)]

    df_accXl = list_of_l[1]['AccX']
    df_accYl = list_of_l[1]['AccY']
    df_accZl = list_of_l[1]['AccZ']
    if len(list_of_l) > 3:
        for df in list_of_l[2:-1]:
            df_accXl = pd.concat((df_accXl.reset_index(drop=True), df['AccX'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
            df_accYl = pd.concat((df_accYl.reset_index(drop=True), df['AccY'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
            df_accZl = pd.concat((df_accZl.reset_index(drop=True), df['AccZ'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
        df_accXl['Mean'] = df_accXl.mean(axis=1)
        df_accYl['Mean'] = df_accYl.mean(axis=1)
        df_accZl['Mean'] = df_accZl.mean(axis=1)

        # do plotting of means
        x_len = len(df_accZl)
        x = np.linspace(0, 1, num=x_len)
        plt.figure(1)
        plt.plot(x, df_accXl['Mean'])
        plt.figure(2)
        plt.plot(x, df_accYl['Mean'])
        plt.figure(3)
        plt.plot(x, df_accZl['Mean'])

        # df_accYl.to_csv("mean_y_accel-" + str(trial_num) + ".csv")
        return df_accYl['Mean'].to_numpy()




def plot_normalised_cycles(data, LHC, RHC, subject, trial_num, save=None):
    """ plot the raw gait signals on a single plot, normalised to the width of the gait cycle """
    # firstly, segment the data into gait cycles using the foot contact points
    l_mod = [0] + LHC + [max(LHC) + 1]
    r_mod = [0] + RHC + [max(RHC) + 1]
    list_of_l = [data.iloc[l_mod[n]:l_mod[n + 1]] for n in range(len(l_mod) - 1)]
    list_of_r = [data.iloc[r_mod[n]:r_mod[n + 1]] for n in range(len(r_mod) - 1)]

    # generate averaged out AccX, AccY and AccZ terms
    df_accXl = list_of_l[1]['AccX']
    df_accYl = list_of_l[1]['AccY']
    df_accZl = list_of_l[1]['AccZ']
    if len(list_of_l) > 3:
        for df in list_of_l[2:-1]:
            df_accXl = pd.concat((df_accXl.reset_index(drop=True), df['AccX'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
            df_accYl = pd.concat((df_accYl.reset_index(drop=True), df['AccY'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
            df_accZl = pd.concat((df_accZl.reset_index(drop=True), df['AccZ'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
        df_accXl['Mean'] = df_accXl.mean(axis=1)
        df_accYl['Mean'] = df_accYl.mean(axis=1)
        df_accZl['Mean'] = df_accZl.mean(axis=1)
        # generate averaged out AccX, AccY and AccZ terms
        df_accXr = list_of_r[1]['AccX']
        df_accYr = list_of_r[1]['AccY']
        df_accZr = list_of_r[1]['AccZ']
        for df in list_of_r[2:-1]:
            df_accXr = pd.concat((df_accXr.reset_index(drop=True), df['AccX'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
            df_accYr = pd.concat((df_accYr.reset_index(drop=True), df['AccY'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
            df_accZr = pd.concat((df_accZr.reset_index(drop=True), df['AccZ'].reset_index(drop=True)), axis=1,
                                 ignore_index=True)
        df_accXr['Mean'] = df_accXr.mean(axis=1)
        df_accYr['Mean'] = df_accYr.mean(axis=1)
        df_accZr['Mean'] = df_accZr.mean(axis=1)
        print(df_accZl)
        print(df_accZr)
        # do plotting of means
        x_len = len(df_accZl)
        x_len2 = len(df_accZr)
        x = np.linspace(0, 1, num=x_len)
        x2 = np.linspace(0, 1, num=x_len2)
        plt.figure(1)
        if subject == "Tom":
            plt.plot(x, -df_accXl['Mean'], 'b')
            plt.plot(x2, -df_accXr['Mean'], 'g')
        else:
            plt.plot(x, df_accXl['Mean'], 'b')
            plt.plot(x2, df_accXr['Mean'], 'g')
        plt.legend(["Left", "Right"])
        plt.figure(2)
        plt.plot(x, df_accYl['Mean'], 'b')
        plt.plot(x2, df_accYr['Mean'], 'g')
        plt.legend(["Left", "Right"])
        plt.figure(3)
        plt.plot(x, df_accZl['Mean'], 'b')
        plt.plot(x2, -df_accZr['Mean'], 'g')
        plt.legend(["Left", "Right"])
        # for i in range(0, len(df_accZl.columns) - 1):
        #     plt.figure()
        #     if subject == "Tom":
        #         plt.plot(x, -df_accXl[i], 'b')#, alpha=0.3)
        #     else:
        #         plt.plot(x, df_accXl[i])#, 'b', alpha=0.3)
        #     plt.title(subject + " " + trial_num + " L vs R gait cycles in X direction")
        #     plt.xlabel("Proportion of gait cycle")
        #     plt.ylabel(r'Acceleration / $ms^{-2}$')
        #     plt.figure(2)
        #     plt.plot(x, df_accYl[i], 'b', alpha=0.3)
        #     plt.title(subject + trial_num + " L vs R gait cycles in Y direction")
        #     plt.xlabel("Proportion of gait cycle")
        #     plt.ylabel(r'Acceleration / $ms^{-2}$')
        #     plt.figure(3)
        #     plt.plot(x, df_accZl[i], 'b', alpha=0.3)
        #     plt.title(subject + trial_num + " L vs R gait cycles in Z direction")
        #     plt.xlabel("Proportion of gait cycle")
        #     plt.ylabel(r'Acceleration / $ms^{-2}$')

        # for i in range(0, len(df_accZr.columns) - 1):
        #     plt.figure(1)
        #     if subject == "Tom":
        #         plt.plot(x2, -df_accXr[i], 'g', alpha=0.3)
        #     else:
        #         plt.plot(x2, df_accXr[i], 'g', alpha=0.3)
        #     plt.figure(2)
        #     plt.plot(x2, df_accYr[i], 'g', alpha=0.3)
        #     plt.figure(3)
        #     plt.plot(x2, -df_accZr[i], 'g', alpha=0.3)
        # plt.show()


def main():
    subject = "Jamie"
    data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/CroppedWalk/"
    og_data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Walk/"
    savedir_plots = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject + "/AllCycles/"
    # ensure folders are there
    try:
        os.mkdir("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject)
    except OSError:
        print("Directory already exists!")
    try:
        os.mkdir(savedir_plots)
    except OSError:
        print("Directory already exists!")
    offset_list = [5, 3, -35, 3, -35, 5]
    count = 0
    all_trial_means = np.zeros((103, 6))
    for file in os.listdir(data_filepath):
        trial_num = file.split('.')[0][-2:] if file.split('.')[0][-2:].isdigit() else file.split('.')[0][-1:]
        if subject == "TomBrace":
            data = pd.read_csv(data_filepath+file, delimiter=',', usecols=[1, 2, 3, 4],
                               names=['Time', 'AccX', 'AccY', 'AccZ'], header=None, skiprows=1)
        else:
            data = pd.read_csv(data_filepath + file, delimiter=',', usecols=[2, 3, 4, 5],
                               names=['Time', 'AccX', 'AccY', 'AccZ'], header=None, skiprows=1)
        # load the ground truth data for the trial
        ground_truth_available = True
        try:
            LHC_gt, RHC_gt, LTO_gt, RTO_gt = load_ground_truth(subject, trial_num)
            # print("LHC_gt: ", LHC_gt)
        except FileNotFoundError:
            print("No ground truth data for trial: ", trial_num)
            ground_truth_available = False
        if ground_truth_available:
            if subject == "TomBrace":
                LHC_gt = [x / 100 for x in LHC_gt]
                RHC_gt = [x / 100 for x in RHC_gt]  # convert to seconds
                # plot_normalised_cycles_time(data, LHC_gt, RHC_gt, subject, trial_num, save=False)
            else:
                # try:
                if int(trial_num) != 2:
                    all_trial_means[:, count] = plot_left_cycles(data, LHC_gt, offset_list[count], trial_num)[:103]
                count +=1
                    # plot_normalised_cycles(data, LHC_gt, RHC_gt, subject, trial_num, save=False)
                # except:
                #     print("Couldn't complete for trial: ", trial_num)

    # deal with the means
    mean_all_trial_means = np.mean(all_trial_means[:, 2:], axis=1)
    all_trial_mins = np.min(all_trial_means[:, 2:], axis=1)
    all_trial_maxes = np.max(all_trial_means[:, 2:], axis=1)
    print(all_trial_mins)
    x = np.linspace(0, 1, num=len(all_trial_means))
    plt.figure(4)
    plt.plot(x, mean_all_trial_means, 'k-', label='_nolegend_')
    # plt.plot(x, all_trial_mins, 'k--')
    # plt.plot(x, all_trial_maxes, 'k--')
    plt.fill_between(x, all_trial_mins, all_trial_maxes, alpha=0.3)
    plt.axvline(x=0, color='r', linestyle='-')
    plt.axvline(x=0.5, color='r', linestyle='-', label='_nolegend_')
    plt.axvline(x=0.088, color='g', linestyle='--')
    plt.axvline(x=0.6, color='g', linestyle='--', label='_nolegend_')
    plt.title(r'Averaged Gait Cycle for Subject A Over 6 Trials', wrap=True, fontsize=40)
    plt.xlabel("Proportion of gait cycle", fontsize=24)
    plt.ylabel(r'Acceleration / $ms^{-2}$', fontsize=24)
    plt.legend(["Range Across Trials", "Heel Strike", "Toe Off"], fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # add legend to summary plots
    for i in range(1,4):
        plt.figure(i)
        plt.legend(["1", "2", "3", "4", "5", "6"])
    plt.show()


if __name__ == "__main__":
    main()