import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


eardatadir = os.getcwd() + "/240214SynchTest"
delsysdatadir = os.getcwd() + "/DelsysData"

earfiles = ["240214SynchTest-01.txt", "240214SynchTest-02.txt", "240214SynchTest-03.txt", "240214SynchTest-04.txt"]
delsysfiles = ["synch01.csv", "synch02.csv", "synch03.csv", "synch04.csv"]
colnames = ["ACCX1", "ACCY1", "ACCZ1", "GYR0X1", "GYROY1", "GYROZ1",
            "ACCX2", "ACCY2", "ACCZ2", "GYR0X2", "GYROY2", "GYROZ2",]
for trial in range(1, 4):
    eardata = pd.read_csv(eardatadir + "/" + earfiles[trial], delimiter=",")
    # format timestamp
    eardata['AccATime'] = eardata['AccATime'] - eardata.iat[0, 1] + 10
    # print(eardata["AccZrear"].corr(eardata["AccZlear"], method='spearman'))
    print(eardata[['AccZrear', 'AccZlear', 'AccZpocket', 'AccZchest']].corr())
    delsysdata = pd.read_csv(delsysdatadir + "/" + delsysfiles[trial], delimiter=",",
                             names=colnames, header=None)#, skiprows=1)
    print(delsysdata.head())
    delsys_time = [int(x) for x in delsysdata.index]

    # Calculate resultant acceleration and gyro vectors ###############
    # accel
    delsys1_acc0 = calculate_acc_zero(delsysdata.iloc[::2, 0:3].values)
    delsys2_acc0 = calculate_acc_zero(delsysdata.iloc[::2, 6:9].values)
    r_acc0 = calculate_acc_zero(eardata.iloc[:, 27:30].values)
    l_acc0 = calculate_acc_zero(eardata.iloc[:, 36:39].values)
    c_acc0 = calculate_acc_zero(eardata.iloc[:, 18:21].values)
    p_acc0 = calculate_acc_zero(eardata.iloc[:, 9:12].values)
    # gyro
    delsys1_gyro0 = calculate_acc_zero(delsysdata.iloc[::2, 3:6].values)
    delsys2_gyro0 = calculate_acc_zero(delsysdata.iloc[::2, 9:12].values)
    r_gyro0 = calculate_acc_zero(eardata.iloc[:, 30:33].values)
    l_gyro0 = calculate_acc_zero(eardata.iloc[:, 39:42].values)
    c_gyro0 = calculate_acc_zero(eardata.iloc[:, 21:24].values)
    p_gyro0 = calculate_acc_zero(eardata.iloc[:, 12:15].values)
    ############################

    # Plot a specific direction #########################
    # plt.plot((eardata['AccATime']+2) % 2**16, eardata['AccXrear'].values)
    # plt.plot((eardata['AccATime']+2) % 2**16, eardata['AccZlear'].values)
    # plt.plot((eardata['AccATime']+1) % 2**16, -eardata['AccZchest'].values)
    # plt.plot((eardata['AccATime']) % 2**16, -eardata['AccZpocket'].values)
    # plt.plot(delsys_time[0:int(len(delsys_time)/2)], delsysdata.loc[::2, 'ACCX1'].values)
    # plt.plot(delsys_time[0:int(len(delsys_time) / 2)], -delsysdata.loc[::2, 'ACCX2'].values)
    ##################################################

    # Plot resultant  accel vector ##########################
    plt.plot((eardata['AccATime'] +2) % 2**16, r_acc0)
    plt.plot((eardata['AccATime'] + 2) % 2 ** 16, l_acc0)
    plt.plot((eardata['AccATime'] + 1) % 2 ** 16, c_acc0)
    plt.plot((eardata['AccATime'] + 0) % 2 ** 16, p_acc0)
    plt.plot(delsys_time[0:int(len(delsys_time) / 2)], delsys1_acc0)
    plt.plot(delsys_time[0:int(len(delsys_time) / 2)], delsys2_acc0)
    ################################################################

    # Plot resultant gyro vector ##########################
    # plt.plot((eardata['AccATime'] + 2) % 2 ** 16, r_gyro0)
    # plt.plot((eardata['AccATime'] + 2) % 2 ** 16, l_gyro0)
    # plt.plot((eardata['AccATime'] + 1) % 2 ** 16, c_gyro0)
    # plt.plot((eardata['AccATime'] + 0) % 2 ** 16, p_gyro0)
    # plt.plot(delsys_time[0:int(len(delsys_time) / 2)], delsys1_gyro0)
    # plt.plot(delsys_time[0:int(len(delsys_time) / 2)], delsys2_gyro0)
    ################################################################

    # Plot aesthetics ################################
    plt.legend(["right", "left", "chest", "pocket", "Delsys1", "Delsys2"])
    # plt.legend(["ear", "delsys1", "delsys2"])
    plt.title("Synchronisation of the ear, chest and pocket IMUs")
    plt.xlabel("Time / ms")
    plt.ylabel("Acceleration / ms")
    plt.show()
    ##############################################


    # calculate the correlations #######################
    # a = eardata['AccZrear'].values
    # b = eardata['AccZpocket'].values * -1
    # correlate_result = np.correlate(a, b, 'full')
    # print(len(correlate_result))
    # b_shift_positions = np.arange(-len(a) + 1, len(b))
    # print(b_shift_positions[int(len(b_shift_positions)/2) - 5 : int(len(b_shift_positions)/2) + 6]) # The shift positions of b
    # print(correlate_result[int(len(b_shift_positions)/2) - 5 : int(len(b_shift_positions)/2) + 6])
    # best_pos = np.argmax(correlate_result)
    # print(b_shift_positions[best_pos])
    ###############################################

