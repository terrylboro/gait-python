# Parse the new data from .txt file into a separate .csv file for each ear
# Assumes right ear is entries 2:10 and left ear is entries 11:19
# Also assumes headset is the new one with x-up, y-forward, z-sideways

import pandas as pd
import numpy as np
import os
import Utils


def parse_new_data(filepath, savedir, filename):
    """ Works for TF_00 (before the timestamps for each value were there) """
    names = ['Frame', 'Time', 'AccXr', 'AccYr', 'AccZr', 'GyroXr', 'GyroYr', 'GyroZr', 'MagXr', 'MagYr', 'MagZr',
             'AccXl', 'AccYl', 'AccZl', 'GyroXl', 'GyroYl', 'GyroZl', 'MagXl', 'MagYl', 'MagZl']
    col_mapper_r = {'Time': 'Time', 'AccXr': 'AccX', 'AccYr': 'AccY', 'AccZr': 'AccZ',
                  'GyroXr': 'GyroX', 'GyroYr': 'GyroY', 'GyroZr': 'GyroZ',
                 'MagXr': 'MagX', 'MagYr': 'MagY', 'MagZr': 'MagZ'}
    col_mapper_l = {'Time': 'Time', 'AccXl': 'AccX', 'AccYl': 'AccY', 'AccZl': 'AccZ',
                    'GyroXl': 'GyroX', 'GyroYl': 'GyroY', 'GyroZl': 'GyroZ',
                    'MagXl': 'MagX', 'MagYl': 'MagY', 'MagZl': 'MagZ'}
    print(len(names))
    print(len(range(0, 20)))
    data = pd.read_csv(filepath, names=names, usecols=range(0, 20))
    data['Time'] = data['Time'].apply(lambda x: x - data.iloc[0, 1])
    print(data['Time'])
    data_r = data.iloc[:, 2:11]
    data_r.insert(0, 'Time', data['Time'])
    data_r.rename(columns=col_mapper_r, inplace=True)
    data_l = data.iloc[:, 11:20]
    data_l.insert(0, 'Time', data['Time'])
    data_l.rename(columns=col_mapper_l, inplace=True)
    # convert to NED
    data_l['AccX'], data_l['AccY'], data_l['AccZ'] = - data_l['AccY'], - data_l['AccZ'], - data_l['AccX']
    data_l['GyroX'], data_l['GyroY'], data_l['GyroZ'] = - data_l['GyroY'], - data_l['GyroZ'], - data_l['GyroX']
    data_l['MagX'], data_l['MagY'], data_l['MagZ'] = - data_l['MagY'], - data_l['MagZ'], - data_l['MagX']
    print(data_l)
    # # current setup ??
    data_r['AccX'], data_r['AccY'], data_r['AccZ'] = - data_r['AccY'], data_r['AccZ'], - data_r['AccX']
    data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = - data_r['GyroY'], data_r['GyroZ'], - data_r['GyroX']
    data_r['MagX'], data_r['MagY'], data_r['MagZ'] = - data_r['MagY'], data_r['MagZ'], - data_r['MagX']
    # # gimbal
    # data_r['AccX'], data_r['AccY'], data_r['AccZ'] = data_r['AccX'], - data_r['AccZ'], - data_r['AccY']
    # data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = data_r['GyroX'], - data_r['GyroZ'], - data_r['GyroY']
    print(data_r)
    data_r.to_csv(savedir+"/Right/"+filename+"_NED.csv", index=False)
    data_l.to_csv(savedir+"/Left/"+filename+"_NED.csv", index=False)


def parse_ear_data(filepath, savedir, filename):
    colNames = open("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/timestampedColumnHeaders",
                         "r").read()
    print(colNames)
    col_mapper_r = {'Time': 'Time', 'AccXrear': 'AccX', 'AccYrear': 'AccY', 'AccZrear': 'AccZ',
                    'GyroXrear': 'GyroX', 'GyroYrear': 'GyroY', 'GyroZrear': 'GyroZ',
                    'MagXrear': 'MagX', 'MagYrear': 'MagY', 'MagZrear': 'MagZ'}
    col_mapper_l = {'Time': 'Time', 'AccXlear': 'AccX', 'AccYlear': 'AccY', 'AccZlear': 'AccZ',
                    'GyroXlear': 'GyroX', 'GyroYlear': 'GyroY', 'GyroZlear': 'GyroZ',
                    'MagXlear': 'MagX', 'MagYlear': 'MagY', 'MagZlear': 'MagZ'}
    data = pd.read_csv(filepath)#, names=colNames)
    # index timing from start of trial
    data['AccCTime'] = data['AccCTime'].apply(lambda x: x - data.loc[0, 'AccCTime'])
    data['AccDTime'] = data['AccDTime'].apply(lambda x: x - data.loc[0, 'AccDTime'])
    l_names = ["AccXlear", "AccYlear", "AccZlear", "GyroXlear", "GyroYlear", "GyroZlear", "MagXlear", "MagYlear", "MagZlear"]
    r_names = ["AccXrear", "AccYrear", "AccZrear", "GyroXrear", "GyroYrear", "GyroZrear", "MagXrear", "MagYrear", "MagZrear"]
    data_r = data[r_names]
    data_r.insert(0, 'Time', data['AccCTime'])
    data_r.rename(columns=col_mapper_r, inplace=True)
    data_l = data[l_names]
    data_l.insert(0, 'Time', data['AccDTime'])
    data_l.rename(columns=col_mapper_l, inplace=True)
    # convert to NED
    data_l['AccX'], data_l['AccY'], data_l['AccZ'] = - data_l['AccY'], - data_l['AccZ'], - data_l['AccX']
    data_l['GyroX'], data_l['GyroY'], data_l['GyroZ'] = - data_l['GyroY'], - data_l['GyroZ'], - data_l['GyroX']
    data_l['MagX'], data_l['MagY'], data_l['MagZ'] = - data_l['MagY'], - data_l['MagZ'], - data_l['MagX']
    # print(data_l)
    if np.mean(data_r['AccX'] < 0):
        # works for TF_01 up to TF_05
        data_r['AccX'], data_r['AccY'], data_r['AccZ'] = - data_r['AccY'], data_r['AccZ'], - data_r['AccX']
        data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = - data_r['GyroY'], data_r['GyroZ'], - data_r['GyroX']
        data_r['MagX'], data_r['MagY'], data_r['MagZ'] = - data_r['MagY'], data_r['MagZ'], - data_r['MagX']
    else:
        # try for TF_06 onwards
        data_r['AccX'], data_r['AccY'], data_r['AccZ'] = data_r['AccY'], data_r['AccZ'], data_r['AccX']
        data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = data_r['GyroY'], data_r['GyroZ'], data_r['GyroX']
        data_r['MagX'], data_r['MagY'], data_r['MagZ'] = data_r['MagY'], data_r['MagZ'], data_r['MagX']
    # # gimbal
    # data_r['AccX'], data_r['AccY'], data_r['AccZ'] = data_r['AccX'], - data_r['AccZ'], - data_r['AccY']
    # data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = data_r['GyroX'], - data_r['GyroZ'], - data_r['GyroY']
    # print(data_r)
    data_r.to_csv(savedir + "/Right/" + filename + "_NED.csv", index=False)
    data_l.to_csv(savedir + "/Left/" + filename + "_NED.csv", index=False)

def parse_multiple_subjects(subjectStart, subjectEnd, activityTypes=["Walk"]):
    # all the subfolders in the "/FilteredData/" folder in a list
    list_subfolders_with_paths = [f.path for f in os.scandir("../../FilteredData/Data/") if f.is_dir()]
    print(list_subfolders_with_paths)
    print(list_subfolders_with_paths[0].split("/")[-1])
    for data_folder in list_subfolders_with_paths[subjectStart:subjectEnd]:
        for activity in activityTypes:
            savedir = "../Data/" + data_folder.split("/")[-1] + "/" + activity + "/Readings"
            if not os.path.exists("../Data/" + data_folder.split("/")[-1]): os.mkdir("../Data/" + data_folder.split("/")[-1])
            if not os.path.exists("../Data/" + data_folder.split("/")[-1] + "/" + activity):
                os.mkdir("../Data/" + data_folder.split("/")[-1] + "/" + activity)
            if not os.path.exists(savedir): os.mkdir(savedir)
            if not os.path.exists(savedir + "/Right/"): os.mkdir(savedir + "/Right/")
            if not os.path.exists(savedir + "/Left/"): os.mkdir(savedir + "/Left/")
            for file in os.listdir(data_folder + "/" + activity + "/"):
                # print(file)
                # print(data_folder)
                parse_ear_data(data_folder+"/" + activity + "/"+file, savedir, file.split(".")[0])

def main():
    parse_multiple_subjects(0, -1, activityTypes=["WalkShake", "WalkNod", "WalkSlow",
                                                       "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"])
    # subject = "TF_01"
    # filepath = "../../Data/" + subject + "/Walk/"
    # savedir = "../Data/" + subject + "/Walk/Readings/"
    # if not os.path.exists("../Data/" + subject): os.mkdir("../Data/" + subject)
    # if not os.path.exists("../Data/" + subject + "/Walk"): os.mkdir("../Data/" + subject + "/Walk")
    # if not os.path.exists(savedir): os.mkdir(savedir)
    # if not os.path.exists(savedir + "/Right/"): os.mkdir(savedir+ "/Right/")
    # if not os.path.exists(savedir + "/Left/"): os.mkdir(savedir + "/Left/")
    # for file in os.listdir(filepath):
    #     print(file)
    #     parse_ear_data(filepath+file, savedir, file.split(".")[0])


if __name__ == "__main__":
    main()
