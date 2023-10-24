# plot the raw gait signals on a single plot, normalised to the width of the gait cycle

import numpy as np
import pandas as pd
import os
from GroundTruths.Functions.load_ground_truth import load_ground_truth
import matplotlib.pyplot as plt
from sklearn.preprocessing import minmax_scale


def plot_normalised_cycles_basic(data, LHC, RHC, subject, trial_num, save=None):
    """ plot the raw gait signals on a single plot, normalised to the width of the gait cycle """
    # firstly, segment the data into gait cycles using the foot contact points
    l_mod = [0] + LHC + [max(LHC) + 1]
    list_of_dfs = [data.iloc[l_mod[n]:l_mod[n+1]] for n in range(len(l_mod)-1)]
    # print(list_of_dfs)
    for df in list_of_dfs[1:]:
        x_len = len(df)
        if x_len > 0:
            x = np.linspace(0, 1, num=x_len)
            plt.figure(1)
            plt.plot(x, df['AccX'])
            plt.title(subject + " " + trial_num + " Anterior/Posterior")
            plt.xlabel("% of gait cycle")
            plt.ylabel(r'Acceleration / $ms^{-2}$')
            plt.figure(2)
            plt.plot(x, df['AccY'])
            plt.xlabel("% of gait cycle")
            plt.ylabel(r'Acceleration / $ms^{-2}$')
            plt.title(subject + " " + trial_num + " Superior/Inferior")
            plt.figure(3)
            plt.plot(x, df['AccZ'])
            plt.title(subject + " " + trial_num + " Mediolateral")
            plt.xlabel("% of gait cycle")
            plt.ylabel(r'Acceleration / $ms^{-2}$')

    if save:
        save_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject + "/Cycles/"
        try:
            os.mkdir(save_filepath)
        except OSError:
            print("Filepath already exists! Will overwrite file.")
        plt.figure(1)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-ap" + ".png", format="png",
                    dpi=600)
        plt.figure(2)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-si" + ".png", format="png",
                    dpi=600)
        plt.figure(3)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-ml" + ".png", format="png",
                    dpi=600)
        # plt.show()
        plt.close()

    else:
        plt.show()


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
    if(len(list_of_l) > 3):
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
        for i in range(0, len(df_accZl.columns) - 1):
            plt.figure()
            if subject == "Tom":
                plt.plot(x, -df_accXl[i], 'b')#, alpha=0.3)
            else:
                plt.plot(x, df_accXl[i])#, 'b', alpha=0.3)
            plt.title(subject + " " + trial_num + " L vs R gait cycles in X direction")
            plt.xlabel("Proportion of gait cycle")
            plt.ylabel(r'Acceleration / $ms^{-2}$')
            plt.figure(2)
            plt.plot(x, df_accYl[i], 'b', alpha=0.3)
            plt.title(subject + trial_num + " L vs R gait cycles in Y direction")
            plt.xlabel("Proportion of gait cycle")
            plt.ylabel(r'Acceleration / $ms^{-2}$')
            plt.figure(3)
            plt.plot(x, df_accZl[i], 'b', alpha=0.3)
            plt.title(subject + trial_num + " L vs R gait cycles in Z direction")
            plt.xlabel("Proportion of gait cycle")
            plt.ylabel(r'Acceleration / $ms^{-2}$')
        for i in range(0, len(df_accZr.columns) - 1):
            plt.figure(1)
            if subject == "Tom":
                plt.plot(x2, -df_accXr[i], 'g', alpha=0.3)
            else:
                plt.plot(x2, df_accXr[i], 'g', alpha=0.3)
            plt.figure(2)
            plt.plot(x2, df_accYr[i], 'g', alpha=0.3)
            plt.figure(3)
            plt.plot(x2, -df_accZr[i], 'g', alpha=0.3)
        # plt.show()

        if save:
            save_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject + "/Cycles/"
            try:
                os.mkdir(save_filepath)
            except OSError:
                print("Filepath already exists! Will overwrite file.")
            plt.figure(1)
            plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-ap" + ".png", format="png",
                        dpi=600)
            plt.figure(2)
            plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-si" + ".png", format="png",
                        dpi=600)
            plt.figure(3)
            plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-ml" + ".png", format="png",
                        dpi=600)
            # plt.show()
            plt.close()

        else:
            plt.show()



def plot_normalised_cycles_time(data, LHC, RHC, subject, trial_num, save=None):
    """ plot the raw gait signals on a single plot, normalised to the width of the gait cycle """
    # need to convert timestamp of GT to nearest index in IMU data
    # find row with closest value to HC in points column
    for i in range(0, len(LHC)):
        LHC[i] = data.iloc[(data['Time'] - LHC[i]).abs().argsort()[:1]].index.tolist()
    LHC = [i for x in LHC for i in x]
    # repeat for rhc
    for i in range(0, len(RHC)):
        RHC[i] = data.iloc[(data['Time'] - RHC[i]).abs().argsort()[:1]].index.tolist()
    RHC = [i for x in RHC for i in x]

    knee_condition = "Straight Knee: " if trial_num == "2" else "Bent Knee: "

    print("LHC: ", LHC)
    print("RHC: ", RHC)

    # firstly, segment the data into gait cycles using the foot contact points
    l_mod = [0] + LHC + [max(LHC) + 1]
    r_mod = [0] + RHC + [max(RHC) + 1]
    list_of_l = [data.iloc[l_mod[n]:l_mod[n+1]] for n in range(len(l_mod)-1)]
    list_of_r = [data.iloc[r_mod[n]:r_mod[n + 1]] for n in range(len(r_mod) - 1)]

    # generate averaged out AccX, AccY and AccZ terms
    df_accXl = list_of_l[1]['AccX']
    df_accYl = list_of_l[1]['AccY']
    df_accZl = list_of_l[1]['AccZ']
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
    for i in range(0, len(df_accZl.columns)-1):
        plt.figure(1)
        # plt.plot(x, df_accXl[i], 'b', alpha=0.3)
        plt.title(knee_condition + "L vs R gait cycles in X direction")
        plt.xlabel("Proportion of gait cycle")
        plt.ylabel(r'Acceleration / $ms^{-2}$')
        plt.figure(2)
        # plt.plot(x, df_accYl[i], 'b', alpha=0.3)
        plt.title(knee_condition + "L vs R gait cycles in Y direction")
        plt.xlabel("Proportion of gait cycle")
        plt.ylabel(r'Acceleration / $ms^{-2}$')
        plt.figure(3)
        # plt.plot(x, df_accZl[i], 'b', alpha=0.3)
        plt.title(knee_condition + "L vs R gait cycles in Z direction")
        plt.xlabel("Proportion of gait cycle")
        plt.ylabel(r'Acceleration / $ms^{-2}$')
    for i in range(0, len(df_accZr.columns)-1):
        plt.figure(1)
        # plt.plot(x2, df_accXr[i], 'g', alpha=0.3)
        # plt.figure(2)
        # plt.plot(x2, df_accYr[i], 'g', alpha=0.3)
        # plt.figure(3)
        # plt.plot(x2, -df_accZr[i], 'g', alpha=0.3)
    # plt.show()
    # # plot all the data on a graph
    # for df in list_of_l[1:]:
    #     x_len = len(df)
    #     x = np.linspace(0, 1, num=x_len)
    #     if x_len > 0:
    #         plt.figure(1)
    #         plt.plot(x, df['AccX'])
    #         plt.title(subject + " " + trial_num + " Anterior/Posterior")
    #         plt.xlabel("% of gait cycle")
    #         plt.ylabel(r'Acceleration / $ms^{-2}$')
    #         plt.figure(2)
    #         plt.plot(x, df['AccY'])
    #         plt.xlabel("% of gait cycle")
    #         plt.ylabel(r'Acceleration / $ms^{-2}$')
    #         plt.title(subject + " " + trial_num + " Superior/Inferior")
    #         plt.figure(3)
    #         plt.plot(x, - df['AccZ'])
    #         plt.title(subject + " " + trial_num + " Mediolateral")
    #         plt.xlabel("% of gait cycle")
    #         plt.ylabel(r'Acceleration / $ms^{-2}$')
    #
    # for df in list_of_r[1:]:
    #     x_len = len(df)
    #     if x_len > 0:
    #         x = np.linspace(0, 1, num=x_len)
    #         plt.figure(1)
    #         plt.plot(x, df['AccX'])
    #         plt.title(subject + " " + trial_num + " Anterior/Posterior")
    #         plt.xlabel("% of gait cycle")
    #         plt.ylabel(r'Acceleration / $ms^{-2}$')
    #         plt.figure(2)
    #         plt.plot(x, df['AccY'])
    #         plt.xlabel("% of gait cycle")
    #         plt.ylabel(r'Acceleration / $ms^{-2}$')
    #         plt.title(subject + " " + trial_num + " Superior/Inferior")
    #         plt.figure(3)
    #         plt.plot(x, df['AccZ'])
    #         plt.title(subject + " " + trial_num + " Mediolateral")
    #         plt.xlabel("% of gait cycle")
    #         plt.ylabel(r'Acceleration / $ms^{-2}$')

    if save:
        save_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject + "/Cycles/"
        try:
            os.mkdir(save_filepath)
        except OSError:
            print("Filepath already exists! Will overwrite file.")
        plt.figure(1)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-ap-means" + ".png", format="png",
                    dpi=600)
        plt.figure(2)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-si-means" + ".png", format="png",
                    dpi=600)
        plt.figure(3)
        plt.savefig(save_filepath + subject + "-" + str(int(trial_num)) + "-ml-means" + ".png", format="png",
                    dpi=600)
        # plt.show()
        plt.close()

    else:
        plt.show()


def main():
    subject = "Jamie"
    data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/CroppedWalk/"
    og_data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Walk/"
    savedir_plots = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject + "/Cycles/"
    # ensure folders are there
    try:
        os.mkdir("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/" + subject)
    except OSError:
        print("Directory already exists!")
    try:
        os.mkdir(savedir_plots)
    except OSError:
        print("Directory already exists!")
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
                plot_normalised_cycles_time(data, LHC_gt, RHC_gt, subject, trial_num, save=False)
            else:
                try:
                    plot_normalised_cycles(data, LHC_gt, RHC_gt, subject, trial_num, save=False)
                except:
                    print("Couldn't complete for trial: ", trial_num)
        plt.show()


if __name__ == "__main__":
    main()
