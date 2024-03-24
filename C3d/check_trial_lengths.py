import os


import os

import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt


def check_c3d_length(filepath):
    """ Extract Wrist and Shank data from c3d and save in """
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    end_fr = itf.GetVideoFrame(1)
    return end_fr


def check_data_length(filepath):
    data = np.loadtxt(filepath, delimiter=",", skiprows=1)
    return len(data)

def main():
    c3d_filepath = "C:/Users/teri-/Documents/TF_62/TF_62/"
    imu_filepath = "../Data/TF_62/"
    lengths = []
    for path, subdirs, files in os.walk(imu_filepath):
        for name in files:
            subject = name.split(".")[0].split("-")[-1]
            # print(subject)
            print(c3d_filepath + "A096391_62_00" + subject.zfill(2) + ".c3d")
            c3d_length = check_c3d_length(c3d_filepath + "A096391_62_00" + subject.zfill(2) + ".c3d")
            imu_length = check_data_length(os.path.join(path, name))
            lengths.append((c3d_length, imu_length))
            # print(c3d_length)
            # print(imu_length)
            # print(os.path.join(path, name))
            # print


if __name__ == "__main__":
    main()
