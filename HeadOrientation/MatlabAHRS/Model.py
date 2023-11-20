# This module contains the code for the 'Model' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 3/8/23

import numpy as np
import quaternion
import pandas as pd
import ECompass
from scipy.spatial.transform import Rotation as R
from DefaultProperties import *


def model(accelReadings, gyroReadings, magReadings, gyroOffset, linAccelPrior, m, q_plus, iteration):
    """ Execute the 'Model' section of the AHRS algorithm
    Inputs:
    Nx3 FLOAT accelReading\n
    Nx3 FLOAT linAccelPrior\n
    NP ARRAY Float Nx3 gyroReadings\n
    NP Float gyroOffset\n
    QUATERNION q_plus\n
    NP ARRAY Float Nx3 m\n
    bool iteration (During the first iteration, the orientation estimate, q−, is initialized by ecompass)
    Outputs:
    1x3 NP ARRAY gAccel
    1x3 NP ARRAY mGyro
    1x3 NP ARRAY g
    QUATERNION q_minus
    """
    if iteration == 0:
        # q_plus, rPrior = ECompass.eCompass(accelReadings, magReadings)
        q_plus, rPrior = ECompass.eCompassGPT(accelReadings, magReadings)

    q_minus = predict_orientation_not_first(gyroReadings, gyroOffset, q_plus)
    # rPrior = quaternion.as_rotation_matrix(q_minus)
    # rPrior = rPrior.T  # adding the .T makes it a frame transformation and not a point transformation
    # print("rPrior: ", rPrior)
    # rPrior = R.from_quat(q_minus).as_matrix()
    rPrior = quaternion_rotation_matrix(q_minus)
    # print("rPrior: ", rPrior)
    g = est_gravity_from_orientation(rPrior)
    mGyro = est_earth_mag_vector(rPrior, m)
    pLinAccelPrior = calculate_pLinAccelPrior(linAccelPrior)
    gAccel = est_gravity_from_acceleration(accelReadings, pLinAccelPrior)
    return gAccel, mGyro, g, q_minus, pLinAccelPrior


def predict_orientation_not_first(gyroReadings, gyroOffset, q_plus, N=1, fs=200):
    """ Update the previous orientation estimate from the gyroscope
    Inputs:
    Float Nx3 gyroReadings
    Float gyroOffset
    QUATERNION prev. orientation est., q+
    BOOL isFirst
    INT decimation factor, N
    INT sampling freq., fs
    Outputs: new estimated orientation from the gyroscope (q-) """
    # Est. angular change from prev. frame
    # print("gyroReadings in function: ", gyroReadings)
    # print("gyroOffset: ", gyroOffset)
    delta_psi = (gyroReadings - gyroOffset) / fs
    # print("delta_psi: ", delta_psi)
    # Convert angular change to quaternions (using rotvec function)
    # deltaQ = quaternion.from_rotation_vector(delta_psi)
    deltaQ = R.from_rotvec(delta_psi).as_quat()

    # print("Delta Q: ", deltaQ)
    # print("Delta Q2: ", deltaQ2)
    # Update prev. orientation est. by rotating it by deltaQ
    # print("q_plus: ", q_plus)
    # q_minus = q_plus * deltaQ
    q_minus = quaternion_multiply(q_plus, deltaQ)
    # print("qorient: ", q_minus)
    return q_minus


def est_gravity_from_orientation(rPrior):
    """ Estimate gravity from orientation
    \nInputs:\n np.array(3x3) rPrior
    \nOutputs: 1x3 FLOAT g """
    g = -1 * rPrior[:, 2] * 9.81  # 9.80665
    # g = -1 * rPrior[:, 2]
    # g *= -9.8
    # reshape the matrix to (3, ) to get rid of nested []
    # g = np.reshape(g, 3)
    return g


def est_gravity_from_acceleration(accelReadings, pLinAccelPrior):
    """ Estimate gravity from current and prev. accelerometer readings
    Inputs: 1x3 FLOAT accelReadings, linAccelPrior
    Outputs: 1x3 FLOAT gAccel """
    # subtract decayed linear accel. est. of prev. iteration from accel readings
    # gAccel = - (accelReadings - linAccelPrior)  # the plus sign is simplification of - (accelReadings - linAccelPrior)
    # pLinAccelPrior = LinearAccelerationDecayFactor * linAccelPrior
    # print("pLinAccelPrior", pLinAccelPrior)
    gAccel = pLinAccelPrior - accelReadings
    # gAccel = - accelReadings + LinearAccelerationDecayFactor * linAccelPrior  # the plus sign is simplification of - (accelReadings - linAccelPrior)
    return gAccel


def est_earth_mag_vector(rPrior, m):
    """ Estimate Earth's magnetic vector from orientation and mag readings 
    \nInputs:
    \n(QUATERNION) np.array(3x3) q_minus
    \n1x3 FLOAT m
    \nOutputs: \n1x3 FLOAT mGyro """
    # Earth's mag. vector estimated by rotating mag. vector est. from prev. iteration
    # by a priori orientation est. in rotation matrix form
    mGyro = np.matmul(rPrior, m.T).T
    # reshape the matrix to (3, ) to get rid of nested []
    mGyro = np.reshape(mGyro, 3)
    return mGyro


def calculate_pLinAccelPrior(linAccelPrior):
    pLinAccelPrior = LinearAccelerationDecayFactor * linAccelPrior
    return pLinAccelPrior


def quaternion_rotation_matrix(Q):
    """
    Covert a quaternion into a full three-dimensional rotation matrix.

    Input
    :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3)

    Output
    :return: A 3x3 element matrix representing the full 3D rotation matrix.
             This rotation matrix converts a point in the local reference
             frame to a point in the global reference frame.
    """
    # normalise first
    Q = quaternion_normalise(Q)

    # print("Q to rot:", Q)

    # Extract the values from Q
    a = Q[3]
    b = Q[0]
    c = Q[1]
    d = Q[2]
    # print(a)

    r00 = 2 * a ** 2 - 1 + 2 * b ** 2
    r01 = 2 * b * c + 2 * a * d
    r02 = 2 * b * d - 2 * a * c
    # Second row
    r10 = 2 * b * c - 2 * a * d
    r11 = 2 * a ** 2 - 1 + 2 * c ** 2
    r12 = 2 * c * d + 2 * a * b
    # Bottom row
    r20 = 2 * b * d + 2 * a * c
    r21 = 2 * c * d - 2 * a * b
    r22 = 2 * a ** 2 - 1 + 2 * d ** 2

    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])

    return rot_matrix

def quaternion_multiply(Q1, Q2):
    # 0, 1, 2, 3
    # 3, 0, 1, 2

    w = Q1[3] * Q2[3] - Q1[0] * Q2[0] - Q1[1] * Q2[1] - Q1[2] * Q2[2]
    x = Q1[3] * Q2[0] + Q1[0] * Q2[3] + Q1[1] * Q2[2] - Q1[2] * Q2[1]
    y = Q1[3] * Q2[1] - Q1[0] * Q2[2] + Q1[1] * Q2[3] + Q1[2] * Q2[0]
    z = Q1[3] * Q2[2] + Q1[0] * Q2[1] - Q1[1] * Q2[0] + Q1[2] * Q2[3]
    return np.array([x, y, z, w])


def quaternion_normalise(q):
    n = np.linalg.norm(q)
    q /= n
    return q


# Module testing
def main():
    data = pd.read_csv('demo-head.csv')
    accel = data[['accel_x', 'accel_y', 'accel_z']].values
    gyro = data[['gyro_x', 'gyro_y', 'gyro_z']].values
    accelReadings = accel[2, :]
    gyroReadings = gyro[2, :]
    magReadings = data[['mag_x', 'mag_y', 'mag_z']].values
    linAccelPrior = np.zeros((1, 3))
    gyroOffset = np.array([0.02, -0.01, -0.02])
    m = np.empty((1, 3))
    m[:] = magReadings[2, :]
    a = np.asarray([1, 0, 0, -0.12755217015525], dtype=np.double)
    q_plus = quaternion.as_quat_array(a)
    print(model(accelReadings, gyroReadings, magReadings, gyroOffset, linAccelPrior, m, q_plus, iteration=0))


if __name__ == "__main__":
    # execute main
    main()



