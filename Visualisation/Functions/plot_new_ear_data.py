# Use this file to plot the new data which has been collected
# Written by Terry Fawden 4/9/2023

from Visualisation.Functions.plot_gait_data import plot_gait_data
import os
from Processing.Common.tilt_correct import *
import matplotlib.pyplot as plt
import pandas as pd


def plot_new_ear_data(load_dir, rot_mat=None, save_dir=None):
    """
    Plot and save all the newly collected data
    :param load_dir: Location of gait trial data from a single subject
    :param save_dir: Location to save plots
    :param side: Select which ear the data is from
    :param rot_mat: Supply the rotation matrix to plot tilt-corrected data
    :return: Nothing (but saves plots into a new folder)
    """
    cols = [2, 3, 4, 11, 12, 13]
    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/columnHeaders", delimiter=',',
                          dtype=str)
    for filename in os.listdir(load_dir):
        print("Hello")
        f = os.path.join(load_dir, filename)
        print(f)
        # checking if it is a file
        if os.path.isfile(f):
            # data = np.loadtxt(f, delimiter=',', usecols=cols)
            data = pd.read_csv(f, names=colNames, skiprows=1)
            data = data.iloc[:, cols]
            print(data)
            # if rot_mat is None:
            #     # Plot the raw data
            #     title = os.path.splitext(filename)[0] + "-" + side
            #     plot_gait_data(data, title)
            #     plt.show()
            # else:
            #     # tilt-correct the data
            #     if side == "right":
            #         data = apply_calibration(rot_mat, data)
            #     else:
            #         data = apply_calibration(rot_mat, align_left_to_global(data))
            title = os.path.splitext(filename)[0]
            # plotted_data = np.zeros_like(data)
            # plotted_data[:, 0] = data[:, 1]
            # plotted_data[:, 1] = - data[:, 2]
            # plotted_data[:, 2] = data[:, 0]
            plot_gait_data(data, title, save_dir)
            if save_dir is None:
                plt.show()



def main():
    subject = "TF_00"
    # First, plot the new data raw
    load_dir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/TF_00/Static/"
    raw_save_dir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/"+subject+"/Uncorrected/"
    corrected_save_dir = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/"+subject+"/Corrected/"
    try:
        os.mkdir("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Visualisation/"+subject+"/")
    except OSError as error:
        print(error)
    try:
        os.mkdir(raw_save_dir)
    except OSError as error:
        print(error)
    try:
        os.mkdir(corrected_save_dir)
    except OSError as error:
        print(error)

    plot_new_ear_data(load_dir)

    # # Then, plot the calibrated data
    # right_static_data = np.loadtxt(load_dir+subject+"-static.txt", delimiter=',', usecols=[2, 3, 4])
    # left_static_data = np.loadtxt(load_dir+subject+"-static.txt", delimiter=',', usecols=[11, 12, 13])
    # right_rot_mat = calculate_rotation_matrix(right_static_data)
    # left_rot_mat = calculate_rotation_matrix(align_left_to_global(left_static_data))
    # plot_new_ear_data(load_dir, corrected_save_dir, "right", right_rot_mat)
    # plot_new_ear_data(load_dir, corrected_save_dir, "left", left_rot_mat)




if __name__ == "__main__":
    main()

