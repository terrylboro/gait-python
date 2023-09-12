# A script to correct for the offset of the IMUs on the headset and align
# their directions with the global co-ordinates system
# Written by Terry Fawden 2/9/2023

import numpy as np
import matplotlib.pyplot as plt




def calculate_rotation_matrix(data):
    """
    A script to correct for the offset of the IMUs on the headset and align
    their directions with the global co-ordinates system.\n
    Based on answer here:\n
    https://stackoverflow.com/questions/76378492/how-to-calculate-rotation-matrix-for-an-accelerometer-using-only-basic-algebraic
    :param data: XYZ from the accelerometer static trial
    :return: Rotation matrix which aligns trial data according to gravity
    """
    # Define axes as constants for convenience and readability
    X_AXIS = 0
    Y_AXIS = 1
    Z_AXIS = 2

    raw_x = np.mean(data[:, 0])
    raw_y = np.mean(data[:, 2])
    raw_z = np.mean(data[:, 1])

    r = np.sqrt(raw_x ** 2 + raw_y ** 2 + raw_z ** 2)

    x = raw_x / r
    y = raw_y / r
    z = raw_z / r

    # g_hat = [0, 0, 1]
    # theta = np.acos(-1 * z)
    # % matrix[X_AXIS][X_AXIS] = (y2 - (x2 * z)) / (x2 + y2);
    # % matrix[X_AXIS][Y_AXIS] = ((-x * y) - (x * y * z)) / (x2 + y2);
    # % matrix[X_AXIS][Z_AXIS] = x;
    # % matrix[Y_AXIS][X_AXIS] = ((-x * y) - (x * y * z)) / (x2 + y2);
    # % matrix[Y_AXIS][Y_AXIS] = (x2 - (y2 * z)) / (x2 + y2);
    # % matrix[Y_AXIS][Z_AXIS] = y;
    # % matrix[Z_AXIS][X_AXIS] = -x;
    # % matrix[Z_AXIS][Y_AXIS] = -y;
    # % matrix[Z_AXIS][Z_AXIS] = -z;
    #

    rot_mat = np.zeros((3, 3))
    rot_mat[X_AXIS, X_AXIS] = (y ** 2 - x ** 2 * z) / (x ** 2 + y ** 2)
    rot_mat[X_AXIS, Y_AXIS] = ((-x * y) - (x * y * z)) / (x ** 2 + y ** 2)
    rot_mat[X_AXIS, Z_AXIS] = x
    rot_mat[Y_AXIS, X_AXIS] = ((-x * y) - (x * y * z)) / (x ** 2 + y ** 2)
    rot_mat[Y_AXIS, Y_AXIS] = (x ** 2 - (y ** 2 * z)) / (x ** 2 + y ** 2)
    rot_mat[Y_AXIS, Z_AXIS] = y
    rot_mat[Z_AXIS, X_AXIS] = -x
    rot_mat[Z_AXIS, Y_AXIS] = -y
    rot_mat[Z_AXIS, Z_AXIS] = -z

    return rot_mat


def apply_calibration(rot_mat, data):
    # Ensure the data aligns correctly
    raw_x = data[:, 0]
    raw_y = data[:, 2]
    raw_z = data[:, 1]

    # Define axes as constants for convenience and readability
    X_AXIS = 0
    Y_AXIS = 1
    Z_AXIS = 2

    # Apply the rotation matrix
    out_x = rot_mat[X_AXIS, X_AXIS] * raw_x + rot_mat[X_AXIS, Y_AXIS] * raw_y + rot_mat[X_AXIS, Z_AXIS] * raw_z
    out_y = rot_mat[Y_AXIS, X_AXIS] * raw_x + rot_mat[Y_AXIS, Y_AXIS] * raw_y + rot_mat[Y_AXIS, Z_AXIS] * raw_z
    out_z = rot_mat[Z_AXIS, X_AXIS] * raw_x + rot_mat[Z_AXIS, Y_AXIS] * raw_y + rot_mat[Z_AXIS, Z_AXIS] * raw_z

    # # Plot for visual comparison
    # plt.figure(1)
    # plt.plot(raw_x)
    # plt.plot(raw_y)
    # plt.plot(raw_z)
    # plt.title("Before Calibration")
    # plt.legend(["x", "y", "z"])
    #
    # plt.figure(2)
    # plt.plot(out_x)
    # plt.plot(out_y)
    # plt.plot(out_z)
    # plt.legend(["x", "y", "z"])
    # plt.title("After Calibration")
    # plt.show()

    # print(out_x.shape)

    return np.concatenate((np.expand_dims(out_x, axis=1), np.expand_dims(out_y, axis=1), np.expand_dims(out_z, axis=1)), axis=1)


def align_left_to_global(data):
    """
    Correct for the positioning of the left IMU to be in line with the right one (and global)
    :param data: Data from left IMU
    :return: Data from left IMU aligned to global co-ordinates
    """
    data[:, 0] = - data[:, 0]
    data[:, 1] = data[:, 1]
    data[:, 2] = - data[:, 2]
    return data


def main():
    filepath = "/Data/Amy/"
    data = np.loadtxt(filepath+"amy-static.txt", delimiter=',', usecols=[2, 3, 4])
    rot_mat = calculate_rotation_matrix(data)
    calibrated_data = apply_calibration(rot_mat, data)
    print(calibrated_data.shape)


if __name__ == "__main__":
    main()

