# plot the knee brace data vs a normal trial

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

from GroundTruths.Functions.load_ground_truth import load_ground_truth


def plot_brace(data, LHC):
    for i in range(0, len(LHC)):
        LHC[i] = data.iloc[(data['Time'] - LHC[i]).abs().argsort()[:1]].index.tolist()
    LHC = [i for x in LHC for i in x]

    # firstly, segment the data into gait cycles using the foot contact points
    l_mod = [0] + LHC + [max(LHC) + 1]
    list_of_l = [data.iloc[l_mod[n]:l_mod[n+1]] for n in range(len(l_mod)-1)]

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

    # do plotting of means
    x_len = len(df_accZl)
    x = np.linspace(0, 1, num=x_len)
    plt.figure(1)
    plt.plot(x, df_accXl['Mean'])
    plt.figure(2)
    plt.plot(x, df_accYl['Mean'] + 10)
    plt.figure(3)
    plt.plot(x, df_accZl['Mean'])

    return df_accYl['Mean']




def plot_normal(data, LHC, subject="Tom"):
    # firstly, segment the data into gait cycles using the foot contact points
    l_mod = [0] + LHC + [max(LHC) + 1]
    list_of_l = [data.iloc[l_mod[n]:l_mod[n + 1]] for n in range(len(l_mod) - 1)]
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
        # do plotting of means
        x_len = len(df_accZl)
        x = np.linspace(0, 1, num=x_len)
        plt.figure(1)
        if subject == "Tom" or subject == "20231020-tom":
            plt.plot(x, -df_accXl['Mean'], 'g')
        else:
            plt.plot(x, df_accXl['Mean'], 'g')
        plt.figure(2)
        plt.plot(x, df_accYl['Mean'], 'g')
        plt.figure(3)
        if subject == "Tom":
            plt.plot(x, df_accZl['Mean'], 'g')
        else:
            plt.plot(x, -df_accZl['Mean'], 'g')

        return df_accYl['Mean']

def main():
    normal_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/20231020-tom/CroppedWalk/"
    brace_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/TomBrace/CroppedWalk/"
    knee_condition = "bent"
    save = False
    # Firstly, plot the normal data
    normal_trial_num = "05"
    normal_subject = "20231020-tom"
    normal_data = pd.read_csv(normal_filepath + normal_subject+"-"+str(normal_trial_num)+".txt", delimiter=',', usecols=[2, 3, 4, 5],
                               names=['Time', 'AccX', 'AccY', 'AccZ'], header=None, skiprows=1)
    # LHC_normal, _, _, _ = load_ground_truth(normal_subject, normal_trial_num)
    # LHC_normal = [130, 240, 350, 445]
    LHC_normal = [125, 235, 345, 440]
    # LHC_normal = [74, 184, 294, 406]
    if normal_trial_num == "05":
        offset = 5#25
    elif normal_trial_num == "09":
        offset = 20
    print(LHC_normal)
    LHC_normal = [x + offset for x in LHC_normal]
    normal_data[['AccX', 'AccY', 'AccZ']] = normal_data[['AccX', 'AccY', 'AccZ']] - normal_data[['AccX', 'AccY', 'AccZ']].mean(axis=0)
    normal_y = plot_normal(normal_data, LHC_normal, normal_subject)

    # Then, plot the knee brace data
    straight_data = pd.read_csv(brace_filepath+"tombrace-2.txt", delimiter=',', usecols=[1, 2, 3, 4],
                               names=['Time', 'AccX', 'AccY', 'AccZ'], header=None, skiprows=1)
    straight_data[['AccX', 'AccY', 'AccZ']] = straight_data[['AccX', 'AccY', 'AccZ']] - straight_data[['AccX', 'AccY', 'AccZ']].mean(axis=0)
    bent_data = pd.read_csv(brace_filepath + "tombrace-4.txt", delimiter=',', usecols=[1, 2, 3, 4],
                                names=['Time', 'AccX', 'AccY', 'AccZ'], header=None, skiprows=1)
    bent_data[['AccX', 'AccY', 'AccZ']] = bent_data[['AccX', 'AccY', 'AccZ']] - bent_data[
        ['AccX', 'AccY', 'AccZ']].mean(axis=0)
    LHC_brace_straight, _, _, _ = load_ground_truth("TomBrace", 2)
    LHC_brace_straight = [x / 100 for x in LHC_brace_straight]
    LHC_brace_bent, _, _, _ = load_ground_truth("TomBrace", 2)
    # LHC_brace_bent = [x + 5 for x in LHC_brace_bent]
    LHC_brace_bent = [x for x in LHC_brace_bent]
    LHC_brace_bent = [x / 100 for x in LHC_brace_bent]
    if knee_condition == "straight":
        plot_brace(straight_data, LHC_brace_straight)
    elif knee_condition == "bent":
        bent_y = plot_brace(bent_data, LHC_brace_bent)
        fig4, (ax1, ax2) = plt.subplots(2, 1)
        # x = np.linspace(0, 1, num=len(bent_y))
        ax1.plot(np.linspace(0, 1, num=len(normal_y)), normal_y)
        ax2.plot(np.linspace(0, 1, num=len(bent_y)), bent_y, 'g')
        ax1.set_ylabel(r'Acceleration / $ms^{-2}$', fontsize=24)
        ax2.set_ylabel(r'Acceleration / $ms^{-2}$', fontsize=24)
        ax2.set_xlabel("Proportion of gait cycle", fontsize=24)
        ax1.set_ylim(-4, 6)
        ax2.set_ylim(-4, 6)
        fig4.suptitle('Typical Gait (Top) vs Gait with Knee Brace (Bottom)', fontsize=40)
        ax1.tick_params(axis='both', which='major', labelsize=18)
        ax2.tick_params(axis='both', which='major', labelsize=18)
        # vlines
        ax1.axvline(x=0, color='r', linestyle='-')
        ax1.axvline(x=0.515, color='r', linestyle='-')
        ax1.axvline(x=0.077, color='r', linestyle='--')
        ax1.axvline(x=0.585, color='r', linestyle='--')
        ax2.axvline(x=0, color='r', linestyle='-')
        ax2.axvline(x=0.528, color='r', linestyle='-')
        ax2.axvline(x=0.073, color='r', linestyle='--')
        ax2.axvline(x=0.577, color='r', linestyle='--')

    elif knee_condition == "both":
        plot_brace(straight_data, LHC_brace_straight)
        plot_brace(bent_data, LHC_brace_bent)


    # label plots etc
    direction = ["X", "Y", "Z"]
    legend_list = [knee_condition.capitalize()] if knee_condition == "straight" or knee_condition == "bent" else ["Straight", "Bent"]
    filename = "straight-and-bent" if knee_condition == "both" else knee_condition
    save_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/TomBrace/Cycles/"
    for i in range(1, 4):
        plt.figure(i)
        plt.title("Impaired vs Usual Gait Cycles in " + direction[i-1] + " Direction")
        plt.xlabel("Proportion of gait cycle")
        plt.ylabel(r'Acceleration / $ms^{-2}$')
        plt.legend(["Usual"] + legend_list)
        if save:
            plt.savefig(save_filepath + direction[i-1] + "-vs-" + filename + ".png", format="png",
                        dpi=300)
    plt.show()


if __name__ == "__main__":
    main()