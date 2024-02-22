import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


eardatadir = os.getcwd() + "/240214SynchTest"
delsysdatadir = os.getcwd() + "/DelsysData"

earfiles = ["240214SynchTest-01.txt", "240214SynchTest-02.txt", "240214SynchTest-03.txt", "240214SynchTest-04.txt"]
delsysfiles = ["SynchTest1.csv", "SynchTest2.csv", "SynchTest3.csv", "SynchTest4.csv"]
for trial in range(0, 1):
    eardata = pd.read_csv(eardatadir + "/" + earfiles[trial], delimiter=",")
    # format timestamp
    eardata['AccATime'] = eardata['AccATime'] - eardata.iat[0, 1] + 10
    # print(eardata["AccZrear"].corr(eardata["AccZlear"], method='spearman'))
    print(eardata[['AccZrear', 'AccZlear', 'AccZpocket', 'AccZchest']].corr())
    delsysdata = pd.read_csv(delsysdatadir + "/" + delsysfiles[trial], delimiter=",")#, skiprows=1)
    print(delsysdata.head())
    delsys_time = [10 * int(x) for x in delsysdata.index]
    # print(10 * map(int,delsysdata.index.tolist()))

    plt.plot(eardata['AccATime']+2, eardata['AccZrear'].values)
    plt.plot(eardata['AccATime']+2, eardata['AccZlear'].values)
    plt.plot(eardata['AccATime']+1, -eardata['AccZchest'].values)
    plt.plot(eardata['AccATime'], -eardata['AccZpocket'].values)
    # plt.plot(delsys_time, -delsysdata['ACCZ1'].values / 10**3)
    plt.plot(int(delsysdata.iloc[::2, 0].values * 100/7.16), -delsysdata.iloc[::2, 4].values / 10 ** 3)


    # plt.plot(range(0, int((len(delsysdata)-1)/2)), delsysdata[1:-1:2, 3] / 1000)
    plt.legend(["right", "left", "chest", "pocket", "Delsys"])
    # plt.legend(["ear", "delsys"])
    plt.show()
    # calculate the correlations
    a = eardata['AccZrear'].values
    b = eardata['AccZpocket'].values * -1
    correlate_result = np.correlate(a, b, 'full')
    print(len(correlate_result))
    b_shift_positions = np.arange(-len(a) + 1, len(b))
    print(b_shift_positions[int(len(b_shift_positions)/2) - 5 : int(len(b_shift_positions)/2) + 6]) # The shift positions of b
    print(correlate_result[int(len(b_shift_positions)/2) - 5 : int(len(b_shift_positions)/2) + 6])
    best_pos = np.argmax(correlate_result)
    print(b_shift_positions[best_pos])

