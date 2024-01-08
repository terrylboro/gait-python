import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from HeadOrientation.MatlabAHRS.plotData import plot_accel, plot_imu_xyz, plot_3axis_data
from Data.Functions.filter_data import filter_data


def view_head_orientation(time, euler_angle_array, title, figNum=None, c=None, legend=None):
    if figNum:
        plt.figure(figNum)
    if c:
        plot_colours = c
    else:
        plot_colours = ['b-', 'r-', 'y-']
    plt.plot(time, euler_angle_array[:, 0], plot_colours[0])
    plt.plot(time, euler_angle_array[:, 1], plot_colours[1])
    plt.plot(time, euler_angle_array[:, 2], plot_colours[2])
    plt.title(title, fontsize=36)
    plt.xlabel("Time / s", fontsize=24)
    plt.ylabel("Euler Angle / deg", fontsize=24)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    if not legend:
        plt.legend(['ψ - Yaw (z)', 'θ - Pitch (y)', 'φ - Roll (x)'])
    else:
        plt.legend(legend, fontsize=20)

# def correct_orientation(rotmat, imu_data):


def preprocess_imu(data):
    accel = data[['AccX', 'AccY', 'AccZ']].values
    gyro = data[['GyroX', 'GyroY', 'GyroZ']].values
    mag = data[['MagX', 'MagY', 'MagZ']].values
    N = np.size(accel, 0)
    # Rearrange the data to fit the correct format
    accelReadings = np.reshape(accel[:, :], (N, 3))
    gyroReadings = np.reshape(gyro[:, :], (N, 3))
    magReadings = np.reshape(mag[:, :], (N, 3))
    return accelReadings, gyroReadings, magReadings

def view_orientation_single_subject():
    subject = "TF_01"
    side = "Left"
    activity = "Walk"
    trials = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 34, 35, 36]
    for trial in trials:
        # file = subject + "-10_NED"
        file = subject + "-" + str(trial).zfill(2) + "_NED"
        img_save_path = "../Data/" + subject + "/" + activity + "/Corrected Graphs/" + side + "/"
        rot_filepath = "../Data/" + subject + "/" + activity + "/Angles/" + side + "/" + file + "-" + side + "-rotmat.csv"
        imu_filepath = "../Data/" + subject + "/" + activity + "/Readings/" + side + "/" + file + ".csv"
        rot_data = pd.read_csv(rot_filepath, skiprows=1, header=None).to_numpy()
        imu_data = pd.read_csv(imu_filepath)
        accelReadings, gyroReadings, magReadings = preprocess_imu(imu_data)
        # Apply rotation correction
        rot_accelReadings = np.zeros((len(accelReadings), 3))
        for i in range(0, len(accelReadings) - 1):
            a = rot_data[i, :].reshape(3, 3)
            # a[:, [0, 1]] = a[:, [1, 0]]
            b = accelReadings[i, :]
            rot_accelReadings[i, :] = np.matmul(a, b)

        # plot_imu_xyz(accelReadings, gyroReadings, magReadings, range(0, len(accelReadings)), "Before",  figNum=1)
        # plot_imu_xyz(rot_accelReadings, gyroReadings, magReadings, range(0, len(accelReadings)), "After", figNum=2)
        plot_accel(range(0, len(accelReadings)), accelReadings,
                   file + " " + side + " " + "Before Head Rotation Compensation", figNum=1)
        plt.savefig(img_save_path + file + " " + side + " " + "Before Head Rotation Compensation.png",
                    bbox_inches="tight")
        plot_accel(range(0, len(accelReadings)), rot_accelReadings,
                   file + " " + side + " " + "After Head Rotation Compensation", figNum=2)
        plt.savefig(img_save_path + file + " " + side + " " + "After Head Rotation Compensation.png",
                    bbox_inches="tight")

def view_orientation_all_subjects(subjectStart, subjectEnd, activityTypes=["Walk"], filter=False):
    # all the subfolders in the "/HeadOrientation/Data/" folder in a list
    list_subfolders_with_paths = [f.path for f in os.scandir("../Data/") if f.is_dir()]
    print(list_subfolders_with_paths)
    for data_folder in list_subfolders_with_paths[subjectStart:subjectEnd]:
        for activity in activityTypes:
            if not os.path.exists(data_folder + "/" + activity + "/Corrected Graphs/"):
                os.mkdir(data_folder + "/" + activity + "/Corrected Graphs/")
            if not os.path.exists(data_folder + "/" + activity + "/Corrected Graphs/Right/"):
                os.mkdir(data_folder + "/" + activity + "/Corrected Graphs/Right/")
            if not os.path.exists(data_folder + "/" + activity + "/Corrected Graphs/Left/"):
                os.mkdir(data_folder + "/" + activity + "/Corrected Graphs/Left/")
        # Produce corrected graphs for the LHS
        for side in ["Left", "Right"]:
            for activity in activityTypes:
                for file in os.listdir(data_folder + "/" + activity + "/Readings/" + side + "/"):
                    img_save_path = data_folder + "/" + activity + "/Corrected Graphs/" + side + "/"
                    rot_filepath = data_folder + "/" + activity + "/Angles/" + side + "/" + file.split(".")[0] + "-" + side + "-rotmat.csv"
                    imu_filepath = data_folder + "/" + activity + "/Readings/" + side + "/" + file
                    rot_data = pd.read_csv(rot_filepath, skiprows=1, header=None).to_numpy()
                    imu_data = pd.read_csv(imu_filepath)
                    accelReadings, gyroReadings, magReadings = preprocess_imu(imu_data)
                    # Apply rotation correction
                    rot_accelReadings = np.zeros((len(accelReadings), 3))
                    for i in range(0, len(accelReadings) - 1):
                        a = rot_data[i, :].reshape(3, 3)
                        # a[:, [0, 1]] = a[:, [1, 0]]
                        b = accelReadings[i, :]
                        rot_accelReadings[i, :] = np.matmul(a, b)

                    # Filter the data
                    if filter:
                        accelReadings, _ = filter_data(accelReadings)
                        rot_accelReadings, _ = filter_data(rot_accelReadings)
                        # using plot_3axis()
                        plot_3axis_data(range(0, len(accelReadings)), accelReadings[:, 0], accelReadings[:, 1],
                                        accelReadings[:, 2], file.split(".")[0] + " " + side + " " +
                                        "\nBefore Rotation Compensation (Filtered)", figNum=1)
                        plt.savefig(img_save_path + file.split(".")[
                            0] + " " + side + " " + "Before Rotation Compensation Filtered.png",
                                    bbox_inches="tight")
                        plot_3axis_data(range(0, len(accelReadings)), rot_accelReadings[:, 0], rot_accelReadings[:, 1],
                                        rot_accelReadings[:, 2], file.split(".")[0] + " " + side + " " +
                                        "\nAfter Rotation Compensation (Filtered)", figNum=2)
                        plt.savefig(img_save_path + file.split(".")[
                            0] + " " + side + " " + "After Rotation Compensation Filtered.png",
                                    bbox_inches="tight")
                        plt.close("all")
                        # plot_accel(range(0, len(accelReadings)), accelReadings,
                        #            file.split(".")[0] + " " + side + " " + "Before Head Rotation Compensation Filtered", figNum=1)
                        # plt.savefig(
                        #     img_save_path + file.split(".")[0] + " " + side + " " + "Before Head Rotation Compensation Filtered.png",
                        #     bbox_inches="tight")
                        # plot_accel(range(0, len(accelReadings)), rot_accelReadings,
                        #            file.split(".")[0] + " " + side + " " + "After Head Rotation Compensation Filtered", figNum=2)
                        # plt.savefig(
                        #     img_save_path + file.split(".")[0] + " " + side + " " + "After Head Rotation Compensation Filtered.png",
                        #     bbox_inches="tight")
                    # Otherwise plot non-filtered data with corresponding titles
                    else:
                        # using plot_3axis()
                        plot_3axis_data(range(0, len(accelReadings)), accelReadings[:, 0], accelReadings[:, 1],
                                        accelReadings[:, 2], file.split(".")[0] + " " + side + " " +
                                        "\nBefore Rotation Compensation", figNum=1)
                        plt.savefig(img_save_path + file.split(".")[
                            0] + " " + side + " " + "Before Rotation Compensation.png",
                                    bbox_inches="tight")
                        plot_3axis_data(range(0, len(accelReadings)), rot_accelReadings[:, 0], rot_accelReadings[:, 1],
                                        rot_accelReadings[:, 2], file.split(".")[0] + " " + side + " " +
                                        "\nAfter Rotation Compensation", figNum=2)
                        plt.savefig(img_save_path + file.split(".")[
                            0] + " " + side + " " + "After Rotation Compensation.png",
                                    bbox_inches="tight")
                        plt.close("all")
                        # using plot_accel() function
                        # plot_accel(range(0, len(accelReadings)), accelReadings,
                        #            file.split(".")[0] + " " + side + " " + "Before Head Rotation Compensation", figNum=1)
                        # plt.savefig(img_save_path + file.split(".")[0] + " " + side + " " + "Before Head Rotation Compensation.png",
                        #             bbox_inches="tight")
                        # plot_accel(range(0, len(accelReadings)), rot_accelReadings,
                        #            file.split(".")[0] + " " + side + " " + "After Head Rotation Compensation", figNum=2)
                        # plt.savefig(img_save_path + file.split(".")[0] + " " + side + " " + "After Head Rotation Compensation.png",
                        #             bbox_inches="tight")

def main():
    view_orientation_all_subjects(1, 14, ["Walk"], filter=False)
    view_orientation_all_subjects(1, 14, ["Walk"], filter=True)



    # for file in os.listdir(filepath):
    #     if "euler" in file:
    #         data = pd.read_csv(filepath + file, skiprows=1, header=None)
    #         print(data.iloc[:, 1])
    #         # view_head_orientation(range(0, len(data)), data["angles"], file)
    #         plot_euler_angles(range(0, len(data)), data.to_numpy(), file)
    #         plt.show()


if __name__ == "__main__":
    main()
