# This module contains the code for the 'Correct' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 16/8/23

import numpy as np
import quaternion
from DefaultProperties import *
from scipy.spatial.transform import Rotation as R


def correct(x_plus, q_minus, prevLinAccelPrior, prevGyroOffset):
    """ Execute the Correct section of the AHRS algorithm
    Inputs:
    x_plus -- np.array
    q_minus -- quaternion
    Outputs:
    orientation -- quaternion
    q_plus -- quaternion
    linAccelPrior -- np.array
    gyroOffset -- np.array
    """
    # Multiply previous estimation by the error
    theta_plus = np.reshape(x_plus[0:3], 3)
    a_plus = np.reshape(x_plus[6:9], 3)
    b_plus = np.reshape(x_plus[3:6], 3)
    # theta_plus = quaternion.from_rotation_vector(theta_plus)  # expeirment with this .T hmm -thetaplus
    theta_plus = quat_conj(R.from_rotvec(theta_plus).as_quat(canonical=True))  # expeirment with this .T
    # print("theta_plus as quaternion: ", theta_plus)
    # print("q_minus: ", q_minus)
    # q_plus = q_minus * theta_plus
    q_plus = quaternion_multiply(q_minus, theta_plus)
    quaternion_normalise(q_plus)
    # q_plus.w = abs(q_plus.w)  # ensure w is always positive

    # print(np.sum(np.sqrt(q_plus ** 2)))
    # q_plus /= np.sqrt(q_plus.w ** 2 + q_plus.x ** 2 + q_plus.y **2 + q_plus.z ** 2)
    # update linear acceleration estimation by decaying the linear acceleration estimation from prev
    # error then subtracting the error
    # print("pLinAccelPrior: ", prevLinAccelPrior)
    # print("linAccelError: ", a_plus)
    linAccelPost = prevLinAccelPrior - a_plus
    # print("pLinAccelPost: ", linAccelPost)
    # est gyro offset by subtracting gyro offset error from gyro offset in prev
    # iteration
    gyroOffset = prevGyroOffset - b_plus
    # assign output variable
    # do I need to normalise this??
    orientation = q_plus
    return orientation, linAccelPost, gyroOffset

def quat_conj(Q):
    """
    Returns the conjugate of the quaternion
    :rtype : Quaternion
    :return: the conjugate of the quaternion
    """
    return np.array([-Q[0], -Q[1], -Q[2], Q[3]])

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

def main():
    x_plus = np.array([[-1.54015344e-02],
     [ 1.10561370e-02],
     [-6.69025025e-02],
     [ 7.70130674e-05],
     [-5.52845580e-05],
     [-3.02112819e-04],
     [-8.76116111e-02],
     [ 3.45547581e-01],
     [ 1.18844533e-01],
     [-4.52693538e-02],
     [ 1.72910192e-01],
     [-3.27170991e-02]],
     dtype=float
    )
    q_minus = quaternion.as_quat_array([0.4, 0.22, 0.36, 0.21])
    prevLinAccelPrior = np.array([2.2, 0.4, 9.0])
    prevGyroOffset = np.array([0.02, 0.01, 0.04])
    orientation, gyroOffset, linAccelPrior = correct(x_plus, q_minus, prevLinAccelPrior, prevGyroOffset)
    print(linAccelPrior)
    print(gyroOffset)
    print(orientation)

if __name__ == "__main__":
    # execute main
    main()
