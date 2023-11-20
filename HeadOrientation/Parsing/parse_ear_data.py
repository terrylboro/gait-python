# Parse the new data from .txt file into a separate .csv file for each ear
# Assumes right ear is entries 2:10 and left ear is entries 11:19
# Also assumes headset is the new one with x-up, y-forward, z-sideways

import pandas as pd
import numpy as np
import os


def parse_new_data(filepath, savedir, filename):
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


def main():
    subject = "TF_00"
    filepath = "../../Data/" + subject + "/Walk/"
    savedir = "../Data/" + subject + "/Walk/Readings/"
    try:
        os.mkdir(savedir)
    except OSError:
        print("Directory: " + savedir + " already exists")
    for file in os.listdir(filepath):
        print(file)
        parse_new_data(filepath+file, savedir, file.split(".")[0])


if __name__ == "__main__":
    main()
