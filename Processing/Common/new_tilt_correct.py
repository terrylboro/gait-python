# A script to correct for the offset of the IMUs on the headset and align
# their directions with the global co-ordinates system
# Written by Terry Fawden 8/2/2024

import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from scipy.signal import filtfilt, butter
from Visualisation.Functions.plot_imu_xyz import plot_imu_xyz


def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def plot_vertical_component(data):
    gravity = np.mean(data, axis=0)
    print(gravity)
    d = data - gravity
    print(len(d))
    # projection, p of d in vertical axis v
    gravity_dot = np.dot(gravity, gravity)
    gravity_norm = np.linalg.norm(gravity)
    # p = np.ones_like(d)
    p = np.ones(len(data))
    h = np.ones(len(data))
    for i in range(0, len(d)):
        p[i] = (np.dot(d[i, :], gravity)) / gravity_norm
        h[i] = np.linalg.norm(d[i, :] - (np.dot(d[i, :], gravity)) / gravity_dot * gravity)
    print(p.shape)
    return p, h


def filter_trial(data, freq):
    b, a = butter(2, freq, btype="low", fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)


def tilt_correct(data, acc_zero):
    gravity = np.mean(data, axis=0)
    sq_acc_total = np.mean(np.square(acc_zero))
    forward_contrib = np.mean(np.square((gravity[0]))) / sq_acc_total
    sideways_contrib = np.mean(np.square((gravity[1]))) / sq_acc_total
    vertical_contrib = np.mean(np.square((gravity[2]))) / sq_acc_total
    # print("sideways contrib: ", sideways_contrib)
    # print("forward contrib: ", forward_contrib)
    # print("upwards contrib: ", vertical_contrib)
    correct_ratio = forward_contrib / (forward_contrib + sideways_contrib)
    # print("correction ratio: ", correct_ratio)

    # apply vertical correction in 2D
    tilt_dot = np.dot(gravity[[0, 2]] / np.linalg.norm(gravity[[0, 2]]), [0., np.mean(acc_zero)]/ np.linalg.norm(np.mean(acc_zero)))
    forward_tilt_angle = np.arccos(tilt_dot) if np.mean(gravity[0]) > 0 else - np.arccos(tilt_dot)
    # forward_tilt_angle = np.arccos(tilt_dot) if np.mean(gravity[0]) < 0 else - np.arccos(tilt_dot)
    # account for fact that some differences may be in the ML plane
    ang_correct_factor = correct_ratio
    # rotate AP and SI in 2D
    rotMatForward = np.array([[np.cos(forward_tilt_angle * ang_correct_factor), -np.sin(forward_tilt_angle * ang_correct_factor)],
                       [np.sin(forward_tilt_angle * ang_correct_factor), np.cos(forward_tilt_angle * ang_correct_factor)]])
    for row in range(0, len(data)):
        data[row, [0, 2]] = np.dot(rotMatForward, data[row, [0, 2]].T)

    # apply side-to-side correction
    tilt_dot = np.dot(gravity[[1, 2]] / np.linalg.norm(gravity[[1, 2]]),
                      [0., np.mean(acc_zero)] / np.linalg.norm(np.mean(acc_zero)))
    sideways_tilt_angle = - np.arccos(tilt_dot) if np.mean(gravity[1]) < 0 else np.arccos(tilt_dot)
    # account for fact that some differences may be in the ML plane
    ang_correct_factor = 1
    # rotate AP and ML in 2D
    rotMatSideways = np.array(
        [[np.cos(sideways_tilt_angle * ang_correct_factor), -np.sin(sideways_tilt_angle * ang_correct_factor)],
         [np.sin(sideways_tilt_angle * ang_correct_factor), np.cos(sideways_tilt_angle * ang_correct_factor)]])
    for row in range(0, len(data)):
        data[row, [1, 2]] = np.dot(rotMatSideways, data[row, [1, 2]].T)
    # plot the result of the transformation
    # plt.figure()
    # plt.plot(data)
    # plt.title("Transformed Data")
    # plt.legend(["X", "Y", "Z"])
    # plt.show()
    return rotMatForward, rotMatSideways


def tilt_correct_multiple_with_save(subjectStart, subjectEnd):
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        if not os.path.exists("../../TiltCorrectedData/" + subject + "/"): os.mkdir("../../TiltCorrectedData/" + subject + "/")
        sides = ["Left", "Right", "Chest", "Pocket"]
        # sides = ["Left"]
        activities = [
            "Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
                      "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp",
                     "Floor2Turf", "Turf2Floor", "ShoeBox"
        ]
        for side in sides:
            if side == "Right" and subject_num == 14:
                loaddir = "../../NEDData/" + subject + "/Static/Left/"
            else:
                loaddir = "../../NEDData/" + subject + "/Static/" + side + "/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                acc_data = pd.read_csv(filepath, usecols=['AccX', 'AccY', 'AccZ']).values
                # find the resultant vector
                acc_zero = calculate_acc_zero(acc_data)
                rotMatForward, rotMatSideways = tilt_correct(acc_data, acc_zero)
            for activity in activities:
                trialdir = "../../NEDData/" + subject + "/" + activity + "/" + side + "/"
                savedir = "../../TiltCorrectedData/" + subject + "/" + activity + "/" + side + "/"
                if not os.path.exists("../../TiltCorrectedData/" + subject + "/" + activity): os.mkdir(
                    "../../TiltCorrectedData/" + subject + "/" + activity)
                if not os.path.exists(savedir): os.mkdir(savedir)
                for trial in os.listdir(trialdir):
                    trial_fp = trialdir + trial
                    trialAccData = pd.read_csv(trial_fp, usecols=['AccX', 'AccY', 'AccZ']).values
                    trialGyroData = pd.read_csv(trial_fp, usecols=['GyroX', 'GyroY', 'GyroZ']).values
                    trialMagData = pd.read_csv(trial_fp, usecols=['MagX', 'MagY', 'MagZ']).values
                    for row in range(0, len(trialAccData)):
                        trialAccData[row, [0, 2]] = np.dot(rotMatForward, trialAccData[row, [0, 2]].T)
                        trialGyroData[row, [0, 2]] = np.dot(rotMatForward, trialGyroData[row, [0, 2]].T)
                        trialMagData[row, [0, 2]] = np.dot(rotMatForward, trialMagData[row, [0, 2]].T)
                    for row in range(0, len(trialAccData)):
                        trialAccData[row, [1, 2]] = np.dot(rotMatSideways, trialAccData[row, [1, 2]].T)
                        trialGyroData[row, [1, 2]] = np.dot(rotMatSideways, trialGyroData[row, [1, 2]].T)
                        trialMagData[row, [1, 2]] = np.dot(rotMatSideways, trialMagData[row, [1, 2]].T)
                    # for TF_14 right
                    # trialAccData[:, [2, 0]] = trialAccData[:, [0, 2]]
                    # trialGyroData[:, [2, 0]] = trialGyroData[:, [0, 2]]
                    # trialMagData[:, [2, 0]] = trialMagData[:, [0, 2]]
                    transformed_arr = np.concatenate((trialAccData, trialGyroData, trialMagData), axis=1)
                    transformed_df = pd.DataFrame(
                        data=transformed_arr,
                        index=None,
                        columns=['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
                    )
                    # np.savetxt("NEDwalk.csv", transformed_arr, delimiter=",")
                    transformed_df.to_csv(savedir+trial, index=False)
                    # plt.show()


def tilt_correct_ntf_save(subjectRange):
    for subject_num in subjectRange:
        subject = "NTF_" + str(subject_num).zfill(2)
        if not os.path.exists("../../TiltCorrectedData/" + subject + "/"): os.mkdir("../../TiltCorrectedData/" + subject + "/")
        sides = ["Left", "Right", "Chest", "Pocket"]
        # sides = ["Left"]
        activities = ["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow",
                      "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp",
                    "Turf2Floor", "Floor2Turf", "ShoeBox"]
        for side in sides:
            loaddir = "../../NEDData/" + subject + "/Static/" + side + "/"
            for file in os.listdir(loaddir):
                filepath = loaddir + file
                acc_data = pd.read_csv(filepath, usecols=['AccX', 'AccY', 'AccZ']).values
                # find the resultant vector
                acc_zero = calculate_acc_zero(acc_data)
                rotMatForward, rotMatSideways = tilt_correct(acc_data, acc_zero)
            for activity in activities:
                trialdir = "../../NEDData/" + subject + "/" + activity + "/" + side + "/"
                savedir = "../../TiltCorrectedData/" + subject + "/" + activity + "/" + side + "/"
                if not os.path.exists("../../TiltCorrectedData/" + subject + "/" + activity): os.mkdir(
                    "../../TiltCorrectedData/" + subject + "/" + activity)
                if not os.path.exists(savedir): os.mkdir(savedir)
                for trial in os.listdir(trialdir):
                    trial_fp = trialdir + trial
                    trialAccData = pd.read_csv(trial_fp, usecols=['AccX', 'AccY', 'AccZ']).values
                    trialGyroData = pd.read_csv(trial_fp, usecols=['GyroX', 'GyroY', 'GyroZ']).values
                    trialMagData = pd.read_csv(trial_fp, usecols=['MagX', 'MagY', 'MagZ']).values
                    for row in range(0, len(trialAccData)):
                        trialAccData[row, [0, 2]] = np.dot(rotMatForward, trialAccData[row, [0, 2]].T)
                        trialGyroData[row, [0, 2]] = np.dot(rotMatForward, trialGyroData[row, [0, 2]].T)
                        trialMagData[row, [0, 2]] = np.dot(rotMatForward, trialMagData[row, [0, 2]].T)
                    for row in range(0, len(trialAccData)):
                        trialAccData[row, [1, 2]] = np.dot(rotMatSideways, trialAccData[row, [1, 2]].T)
                        trialGyroData[row, [1, 2]] = np.dot(rotMatSideways, trialGyroData[row, [1, 2]].T)
                        trialMagData[row, [1, 2]] = np.dot(rotMatSideways, trialMagData[row, [1, 2]].T)
                    # for TF_14 right
                    # trialAccData[:, [2, 0]] = trialAccData[:, [0, 2]]
                    # trialGyroData[:, [2, 0]] = trialGyroData[:, [0, 2]]
                    # trialMagData[:, [2, 0]] = trialMagData[:, [0, 2]]
                    transformed_arr = np.concatenate((trialAccData, trialGyroData, trialMagData), axis=1)
                    transformed_df = pd.DataFrame(
                        data=transformed_arr,
                        index=None,
                        columns=['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
                    )
                    # np.savetxt("NEDwalk.csv", transformed_arr, delimiter=",")
                    transformed_df.to_csv(savedir+trial, index=False)
                    # plt.show()


def tilt_correct_multiple(subjectStart, subjectEnd):
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        sides = ["Left", "Right"]
        # sides = ["Left"]
        for side in sides:
            loaddir = "../../NEDData/" + subject + "/Static/" + side + "/"
            for file in os.listdir(loaddir):
                # if file.split("_")[1][-1] == str(2):
                filepath = loaddir + file
                acc_data = pd.read_csv(filepath, usecols=['AccX', 'AccY', 'AccZ']).values
                # find the resultant vector
                acc_zero = calculate_acc_zero(acc_data)
                p, _ = plot_vertical_component(acc_data)
                # apply low pass filtering
                # acc_data = filter_trial(acc_data, 0.1)
                # filtered_acc_zero = filter_trial(acc_zero, 0.1)
                # plt.plot(acc_zero)
                # plt.plot(range(0, len(p)), p)
                plt.plot(acc_data)
                plt.title(file + " " + side)
                plt.legend(["X", "Y", "Z"])
                # plt.show()
                rotMatForward, rotMatSideways = tilt_correct(acc_data, acc_zero)
                # Plot the original and rotation corrected data
                trialdir = "../../NEDData/" + subject + "/Walk/" + side + "/"
                for trial in os.listdir(trialdir):
                    if trial == os.listdir(trialdir)[1]:
                        trial_fp = trialdir + trial
                        trialAccData = pd.read_csv(trial_fp, usecols=['AccX', 'AccY', 'AccZ']).values
                        trialGyroData = pd.read_csv(trial_fp, usecols=['GyroX', 'GyroY', 'GyroZ']).values
                        trialMagData = pd.read_csv(trial_fp, usecols=['MagX', 'MagY', 'MagZ']).values
                        # plt.figure()
                        # plt.plot(trialAccData)
                        # plt.title(trial + ": Original Data")
                        plot_imu_xyz(trialAccData, trialGyroData, trialMagData,
                                     np.linspace(0, int(len(trialAccData) / 100), len(trialAccData)),
                                     trial + ": Original Data", legend=["N", "E", "D"])
                        for row in range(0, len(trialAccData)):
                            trialAccData[row, [0, 2]] = np.dot(rotMatForward, trialAccData[row, [0, 2]].T)
                            trialGyroData[row, [0, 2]] = np.dot(rotMatForward, trialGyroData[row, [0, 2]].T)
                            trialMagData[row, [0, 2]] = np.dot(rotMatForward, trialMagData[row, [0, 2]].T)
                            # for subject 14
                            # trialAccData[row, [2, 0]] = trialAccData[row, [2, 0]]
                            # trialGyroData[row, [2, 0]] = np.dot(rotMatForward, trialGyroData[row, [0, 2]].T)
                            # trialMagData[row, [2, 0]] = np.dot(rotMatForward, trialMagData[row, [0, 2]].T)

                        for row in range(0, len(trialAccData)):
                            trialAccData[row, [1, 2]] = np.dot(rotMatSideways, trialAccData[row, [1, 2]].T)
                            trialGyroData[row, [1, 2]] = np.dot(rotMatSideways, trialGyroData[row, [1, 2]].T)
                            trialMagData[row, [1, 2]] = np.dot(rotMatSideways, trialMagData[row, [1, 2]].T)
                        # for TF_14 right
                        # trialAccData[:, [2, 0]] = trialAccData[:, [0, 2]]
                        # trialGyroData[:, [2, 0]] = trialGyroData[:, [0, 2]]
                        # trialMagData[:, [2, 0]] = trialMagData[:, [0, 2]]
                        plot_imu_xyz(trialAccData, trialGyroData, trialMagData,
                                     np.linspace(0, int(len(trialAccData) / 100), len(trialAccData)),
                                     trial + ": Transformed Data", legend=["N", "E", "D"])
                        transformed_arr = np.concatenate((trialAccData, trialGyroData, trialMagData), axis=1)
                        print(transformed_arr.shape)
                        # np.savetxt("NEDwalk.csv", transformed_arr, delimiter=",")
                        plt.figure()
                        plt.plot(trialAccData)
                        plt.plot(np.linspace(0, int(len(trialAccData) / 100), len(trialAccData)), trialAccData[:, 2])
                        plt.title(trial + " Transformed")
                        plt.xlabel("Time / s")
                        plt.ylabel("Accel / m/s^2")
                        plt.legend(["X", "Y", "Z"])
                        plt.show()


def main():
    # tilt_correct_multiple(14, 15)
    tilt_correct_multiple_with_save(65, 66)
    # tilt_correct_ntf_save(range(54, 56))


if __name__ == "__main__":
    main()

