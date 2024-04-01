import os
import pandas as pd
import numpy as np


def parse_data(filepath, savedir, filename):
    # colNames = open("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/timestampedColumnHeaders",
    #                      "r").read()
    colNames = open("../../Utils/reducedColumnHeaders",
                    "r").read()
    print(colNames)
    col_mapper_r = {'Time': 'Time', 'AccXrear': 'AccX', 'AccYrear': 'AccY', 'AccZrear': 'AccZ',
                    'GyroXrear': 'GyroX', 'GyroYrear': 'GyroY', 'GyroZrear': 'GyroZ',
                    'MagXrear': 'MagX', 'MagYrear': 'MagY', 'MagZrear': 'MagZ'}
    col_mapper_l = {'Time': 'Time', 'AccXlear': 'AccX', 'AccYlear': 'AccY', 'AccZlear': 'AccZ',
                    'GyroXlear': 'GyroX', 'GyroYlear': 'GyroY', 'GyroZlear': 'GyroZ',
                    'MagXlear': 'MagX', 'MagYlear': 'MagY', 'MagZlear': 'MagZ'}
    col_mapper_c = {'Time': 'Time', 'AccXchest': 'AccX', 'AccYchest': 'AccY', 'AccZchest': 'AccZ',
                    'GyroXchest': 'GyroX', 'GyroYchest': 'GyroY', 'GyroZchest': 'GyroZ',
                    'MagXchest': 'MagX', 'MagYchest': 'MagY', 'MagZchest': 'MagZ'}
    col_mapper_p = {'Time': 'Time', 'AccXpocket': 'AccX', 'AccYpocket': 'AccY', 'AccZpocket': 'AccZ',
                    'GyroXpocket': 'GyroX', 'GyroYpocket': 'GyroY', 'GyroZpocket': 'GyroZ',
                    'MagXpocket': 'MagX', 'MagYpocket': 'MagY', 'MagZpocket': 'MagZ'}
    data = pd.read_csv(filepath)#, names=colNames)
    # index timing from start of trial
    data['AccATime'] = data['AccATime'].apply(lambda x: x - data.loc[0, 'AccATime'])
    data['AccBTime'] = data['AccBTime'].apply(lambda x: x - data.loc[0, 'AccBTime'])
    data['AccCTime'] = data['AccCTime'].apply(lambda x: x - data.loc[0, 'AccCTime'])
    data['AccDTime'] = data['AccDTime'].apply(lambda x: x - data.loc[0, 'AccDTime'])
    l_names = ["AccXlear", "AccYlear", "AccZlear", "GyroXlear", "GyroYlear", "GyroZlear", "MagXlear", "MagYlear", "MagZlear"]
    r_names = ["AccXrear", "AccYrear", "AccZrear", "GyroXrear", "GyroYrear", "GyroZrear", "MagXrear", "MagYrear", "MagZrear"]
    c_names = ["AccXchest", "AccYchest", "AccZchest", "GyroXchest", "GyroYchest", "GyroZchest", "MagXchest", "MagYchest",
               "MagZchest"]
    p_names = ["AccXpocket", "AccYpocket", "AccZpocket", "GyroXpocket", "GyroYpocket", "GyroZpocket", "MagXpocket",
               "MagYpocket", "MagZpocket"]
    data_r = data[r_names]
    data_r.insert(0, 'Time', data['AccCTime'])
    data_r.rename(columns=col_mapper_r, inplace=True)
    data_l = data[l_names]
    data_l.insert(0, 'Time', data['AccDTime'])
    data_l.rename(columns=col_mapper_l, inplace=True)
    data_c = data[c_names]
    data_c.insert(0, 'Time', data['AccATime'])
    data_c.rename(columns=col_mapper_c, inplace=True)
    data_p = data[p_names]
    data_p.insert(0, 'Time', data['AccBTime'])
    data_p.rename(columns=col_mapper_p, inplace=True)
    # convert to NED
    # left ear
    if np.mean(data_l['AccX'] < 0):
        data_l['AccX'], data_l['AccY'], data_l['AccZ'] = - data_l['AccY'], data_l['AccZ'], - data_l['AccX']
        data_l['GyroX'], data_l['GyroY'], data_l['GyroZ'] = - data_l['GyroY'], data_l['GyroZ'], - data_l['GyroX']
        data_l['MagX'], data_l['MagY'], data_l['MagZ'] = - data_l['MagY'], data_l['MagZ'], - data_l['MagX']
    else:
        data_l['AccX'], data_l['AccY'], data_l['AccZ'] = - data_l['AccY'], - data_l['AccZ'], data_l['AccX']
        data_l['GyroX'], data_l['GyroY'], data_l['GyroZ'] = - data_l['GyroY'], - data_l['GyroZ'], data_l['GyroX']
        data_l['MagX'], data_l['MagY'], data_l['MagZ'] = - data_l['MagY'], - data_l['MagZ'], data_l['MagX']
    # right ear
    if np.mean(data_r['AccX'] < 0):
        # works for TF_01 up to TF_05
        data_r['AccX'], data_r['AccY'], data_r['AccZ'] = data_r['AccY'], data_r['AccZ'], - data_r['AccX']
        data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = data_r['GyroY'], data_r['GyroZ'], - data_r['GyroX']
        data_r['MagX'], data_r['MagY'], data_r['MagZ'] = data_r['MagY'], data_r['MagZ'], - data_r['MagX']
    else:
        # # try for TF_06 onwards
        data_r['AccX'], data_r['AccY'], data_r['AccZ'] = data_r['AccY'], data_r['AccZ'], data_r['AccX']
        data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = data_r['GyroY'], data_r['GyroZ'], data_r['GyroX']
        data_r['MagX'], data_r['MagY'], data_r['MagZ'] = data_r['MagY'], data_r['MagZ'], data_r['MagX']
        # for TF_14
        # data_r['AccX'], data_r['AccY'], data_r['AccZ'] = data_r['AccX'], data_r['AccZ'], -data_r['AccY']
        # data_r['GyroX'], data_r['GyroY'], data_r['GyroZ'] = data_r['GyroX'], data_r['GyroZ'], -data_r['GyroY']
        # data_r['MagX'], data_r['MagY'], data_r['MagZ'] = data_r['MagX'], data_r['MagZ'], -data_r['MagY']
    # chest
    if np.mean(data_c['AccY'] > 0):
        data_c['AccX'], data_c['AccY'], data_c['AccZ'] = data_c['AccZ'], data_c['AccX'], data_c['AccY']
        data_c['GyroX'], data_c['GyroY'], data_c['GyroZ'] = data_c['GyroZ'], data_c['GyroX'], data_c['GyroY']
        data_c['MagX'], data_c['MagY'], data_c['MagZ'] = data_c['MagZ'], data_c['MagX'], data_c['MagY']
    else:
        data_c['AccX'], data_c['AccY'], data_c['AccZ'] = data_c['AccZ'], -data_c['AccX'], -data_c['AccY']
        data_c['GyroX'], data_c['GyroY'], data_c['GyroZ'] = data_c['GyroZ'], -data_c['GyroX'], -data_c['GyroY']
        data_c['MagX'], data_c['MagY'], data_c['MagZ'] = data_c['MagZ'], -data_c['MagX'], -data_c['MagY']
    # pocket
    if np.mean(data_p['AccX'] > 0):
        data_p['AccX'], data_p['AccY'], data_p['AccZ'] = data_p['AccZ'], data_p['AccY'], data_p['AccX']
        data_p['GyroX'], data_p['GyroY'], data_p['GyroZ'] = data_p['GyroZ'], data_p['GyroY'], data_p['GyroX']
        data_p['MagX'], data_p['MagY'], data_p['MagZ'] = data_p['MagZ'], data_p['MagY'], data_p['MagX']
    else:
        data_p['AccX'], data_p['AccY'], data_p['AccZ'] = data_p['AccZ'], -data_p['AccY'], -data_p['AccX']
        data_p['GyroX'], data_p['GyroY'], data_p['GyroZ'] = data_p['GyroZ'], -data_p['GyroY'], -data_p['GyroX']
        data_p['MagX'], data_p['MagY'], data_p['MagZ'] = data_p['MagZ'], -data_p['MagY'], -data_p['MagX']
    # print("saving to:\n")
    # print(savedir + "/Right/" + filename + "_NED.csv")
    data_r.to_csv(savedir + "/Right/" + filename + "_NED.csv", index=False)
    data_l.to_csv(savedir + "/Left/" + filename + "_NED.csv", index=False)
    data_c.to_csv(savedir + "/Chest/" + filename + "_NED.csv", index=False)
    data_p.to_csv(savedir + "/Pocket/" + filename + "_NED.csv", index=False)


def parse_ntf_subjects(subjectRange, activityTypes):
    # all the subfolders in the "/FilteredData/" folder in a list
    subjectSubfolders = []
    for subject in subjectRange:
        subjectSubfolders.append("NTF_" + str(subject).zfill(2) + "/")
    for data_folder in subjectSubfolders:
        for activity in activityTypes:
            savedir = "../../NEDData/" + data_folder + "/" + activity + "/"
            if not os.path.exists("../../NEDData/" + data_folder):
                os.mkdir("../../NEDData/" + data_folder)
            if not os.path.exists("../../NEDData/" + data_folder + "/" + activity):
                os.mkdir("../../NEDData/" + data_folder + "/" + activity)
            if not os.path.exists(savedir): os.mkdir(savedir)
            if not os.path.exists(savedir + "/Right/"): os.mkdir(savedir + "/Right/")
            if not os.path.exists(savedir + "/Left/"): os.mkdir(savedir + "/Left/")
            if not os.path.exists(savedir + "/Chest/"): os.mkdir(savedir + "/Chest/")
            if not os.path.exists(savedir + "/Pocket/"): os.mkdir(savedir + "/Pocket/")
            for file in os.listdir("../../Data/" + data_folder + "/" + activity + "/"):
                print(file)
                print(data_folder)
                parse_data("../../Data/" + data_folder + "/" + activity + "/" + file, savedir, file.split(".")[0])


def parse_tf_subjects(subjectRange, activityTypes):
    # all the subfolders in the "/FilteredData/" folder in a list
    subjectSubfolders = []
    for subject in subjectRange:
        subjectSubfolders.append("TF_" + str(subject).zfill(2) + "/")
    for data_folder in subjectSubfolders:
        for activity in activityTypes:
            savedir = "../../NEDData/" + data_folder + "/" + activity + "/"
            if not os.path.exists("../../NEDData/" + data_folder):
                os.mkdir("../../NEDData/" + data_folder)
            if not os.path.exists("../../NEDData/" + data_folder + "/" + activity):
                os.mkdir("../../NEDData/" + data_folder + "/" + activity)
            if not os.path.exists(savedir): os.mkdir(savedir)
            if not os.path.exists(savedir + "/Right/"): os.mkdir(savedir + "/Right/")
            if not os.path.exists(savedir + "/Left/"): os.mkdir(savedir + "/Left/")
            if not os.path.exists(savedir + "/Chest/"): os.mkdir(savedir + "/Chest/")
            if not os.path.exists(savedir + "/Pocket/"): os.mkdir(savedir + "/Pocket/")
            for file in os.listdir("../../Data/" + data_folder + "/" + activity + "/"):
                print(file)
                print(data_folder)
                parse_data("../../Data/" + data_folder + "/" + activity + "/" + file, savedir, file.split(".")[0])


def parse_multiple_subjects(subjectRange, activityTypes=["Walk"]):
    # all the subfolders in the "/FilteredData/" folder in a list
    list_subfolders_with_paths = [f.path for f in os.scandir("../../FilteredData/Data/") if f.is_dir()]
    print(len(list_subfolders_with_paths))
    print(subjectRange[0])
    print(list_subfolders_with_paths[subjectRange[0]-1].split("/")[-1])
    print(subjectRange)
    subject_subfolders = []
    for subject in range(0, len(subjectRange)):
        subject_subfolders.append(list_subfolders_with_paths[subjectRange[subject]-1])
    for data_folder in subject_subfolders:
        for activity in activityTypes:
            savedir = "../../NEDData/" + data_folder.split("/")[-1] + "/" + activity + "/"
            if not os.path.exists("../../NEDData/" + data_folder.split("/")[-1]):
                os.mkdir("../../NEDData/" + data_folder.split("/")[-1])
            if not os.path.exists("../../NEDData/" + data_folder.split("/")[-1] + "/" + activity):
                os.mkdir("../../NEDData/" + data_folder.split("/")[-1] + "/" + activity)
            if not os.path.exists(savedir): os.mkdir(savedir)
            if not os.path.exists(savedir + "/Right/"): os.mkdir(savedir + "/Right/")
            if not os.path.exists(savedir + "/Left/"): os.mkdir(savedir + "/Left/")
            if not os.path.exists(savedir + "/Chest/"): os.mkdir(savedir + "/Chest/")
            if not os.path.exists(savedir + "/Pocket/"): os.mkdir(savedir + "/Pocket/")
            for file in os.listdir(data_folder + "/" + activity + "/"):
                print(file)
                print(data_folder)
                parse_data(data_folder+"/" + activity + "/"+file, savedir, file.split(".")[0])


def main():
    # activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
    # "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"]
    # parse_multiple_subjects(range(30, 31), activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
    #                                                "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"])
    parse_tf_subjects(range(20, 66), activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
                                                          "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"])#,
                                                    # "ShoeBox", "Turf2Floor", "Floor2Turf"])
    # parse_ntf_subjects(range(54, 56), activityTypes=["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
    #                                                       "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp",
    #                                                  "ShoeBox", "Turf2Floor", "Floor2Turf"])

if __name__ == "__main__":
    main()
