import os
import pandas as pd
import numpy as np

def calculate_acc_zero(data):
    acc_zero_data = np.zeros((len(data), 1))
    for row in range(0, len(data)):
        acc_zero_data[row] = np.sqrt(np.sum(np.square(data[row, :])))
    return acc_zero_data.squeeze()


def rearrange_local_to_NED(oldData, side):
    # Delsys: Arrow points forward in negative Y direction, positive X is down, positive Z is leftwards
    newData = np.empty_like(oldData)
    if side == "Wrist":
        newData[:, 0] = -oldData[:, 0]
        newData[:, 1] = -oldData[:, 2]
        newData[:, 2] = oldData[:, 1]
        return newData
    elif side == "Shank":
        newData[:, 0] = -oldData[:, 1]
        newData[:, 1] = oldData[:, 2]
        newData[:, 2] = -oldData[:, 0]
        return newData
    else:
        print("Side must be wrist or shank")


def tilt_correct(data, acc_zero):
    gravity = np.mean(data, axis=0)
    sq_acc_total = np.mean(np.square(acc_zero))
    forward_contrib = np.mean(np.square((gravity[0]))) / sq_acc_total
    sideways_contrib = np.mean(np.square((gravity[1]))) / sq_acc_total
    vertical_contrib = np.mean(np.square((gravity[2]))) / sq_acc_total
    correct_ratio = forward_contrib / (forward_contrib + sideways_contrib)

    # apply vertical correction in 2D
    tilt_dot = np.dot(gravity[[0, 2]] / np.linalg.norm(gravity[[0, 2]]),
                      [0., np.mean(acc_zero)] / np.linalg.norm(np.mean(acc_zero)))
    forward_tilt_angle = np.arccos(tilt_dot) if np.mean(gravity[0]) > 0 else - np.arccos(tilt_dot)
    # account for fact that some differences may be in the ML plane
    ang_correct_factor = correct_ratio
    # rotate AP and SI in 2D
    rotMatForward = np.array(
        [[np.cos(forward_tilt_angle * ang_correct_factor), -np.sin(forward_tilt_angle * ang_correct_factor)],
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
    return rotMatForward, rotMatSideways


def generic_imu_tilt_correct(dataArr, side):
    # Apply NED correction
    accNEDArr = rearrange_local_to_NED(dataArr[:, 0:3], side)
    gyroNEDArr = rearrange_local_to_NED(dataArr[:, 3:6], side)
    accZero = calculate_acc_zero(accNEDArr)
    # calculate the rotation offset to convert local to global
    rotMatForward, rotMatSideways = tilt_correct(accNEDArr, accZero)
    # apply these rotations to each row
    for row in range(0, len(dataArr)):
        accNEDArr[row, [0, 2]] = np.dot(rotMatForward, accNEDArr[row, [0, 2]].T)
        gyroNEDArr[row, [0, 2]] = np.dot(rotMatForward, gyroNEDArr[row, [0, 2]].T)
        # trialMagData[row, [0, 2]] = np.dot(rotMatForward, trialMagData[row, [0, 2]].T)
    for row in range(0, len(dataArr)):
        accNEDArr[row, [1, 2]] = np.dot(rotMatSideways, accNEDArr[row, [1, 2]].T)
        gyroNEDArr[row, [1, 2]] = np.dot(rotMatSideways, gyroNEDArr[row, [1, 2]].T)
        # trialMagData[row, [1, 2]] = np.dot(rotMatSideways, trialMagData[row, [1, 2]].T)

    rotatedArr = np.concatenate((accNEDArr, gyroNEDArr), axis=1)
    # rotatedDF = pd.DataFrame(
    #     data=rotatedArr,
    #     index=None,
    #     columns=[x + side for x in ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']]
    # )
    return rotatedArr