# A module which implements the eCompass function defined here:
# https://uk.mathworks.com/help/fusion/ref/ecompass.html#mw_13399783-e8e8-4c5d-b605-f19d01e0a444
# This is used to initialise q_plus on the first pass of the Kalman Filter algorithm
# Written by Terry Fawden 17/8/2023

import numpy as np
import quaternion
from scipy.spatial.transform import Rotation as R

def eCompass(a, m):
    """ Orientation from magnetometer and accelerometer readings
    \nInputs:\n
    a -- accelerometer readings\n
    m -- magnetometer readings\n
    Outputs:\n
    (q, R) -- orientation in quaternion and rotation matrix form"""
    R = np.empty((3, 3))
    R[:, 2] = a.T  # since gravity is in z- axis, 3rd column corresponds to accel reading
    # E-axis is perpendicular to N-D plane so a x m = y direction
    R[:, 1] = np.cross(a, m)
    # By definition, column 1 is cross product of 2 and 3
    R[0:, 0] = np.cross(R[:, 1], R[:, 2])
    # Normalise the rotation matrix
    col_denom = np.sqrt(np.sum(np.square(R), axis=0))
    for i in range(0, 2):
        R[:, i] /= col_denom[i]

    # qw = np.sqrt(1 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
    # qx = (R[2, 1] - R[1, 2]) / (4 * qw)
    # qy = (R[0, 2] - R[2, 0]) / (4 * qw)
    # qz = (R[1, 0] - R[0, 1]) / (4 * qw)
    # q = quaternion.as_quat_array([qw, qx, qy, qz])
    # note that the matrix is normalised by the function
    # so when we convert back to rotmat form we must multiply the last column by 9.8
    q = quaternion.from_rotation_matrix(R.T)  # .T seems to make the output match MATLAB's (likely point vs frame)
    # from reverse engineering the ecompass on matlab
    # q = quaternion.as_quat_array([0.17802, -0.15116, 0.97211, -0.021536])
    # R = np.array([[-0.8908], [-0.3015], [-0.3396],
    #              [-0.2862], [0.9534], [-0.0957],
    #              [0.3526], [0.0119], [-0.9357]
    #              ]).reshape((3, 3))
    return q, R

def eCompassGPT(accel, mag):
    """Compute the 3D orientation of a device from its accelerometer and magnetometer data."""
    # down = -accel / np.linalg.norm(accel)
    down = accel / np.linalg.norm(accel)
    east = np.cross(down, mag)
    east /= np.linalg.norm(east)
    north = np.cross(east, down)
    rot_matrix = np.vstack([north, east, down])
    rotation = R.from_matrix(rot_matrix)
    euler_angles = rotation.as_euler('zyx', degrees=True)
    q = R.from_matrix(rot_matrix).as_quat(canonical=True)
    return q, euler_angles

def main():
    # determine magnetic declination of Boston
    # returns [14.6563, 0, 0] if correct
    magneticFieldStrength = np.array([19.535, - 5.109, 47.930])
    properAcceleration = np.array([0, 0, 9.8])
    # magneticFieldStrength = np.array([1, 0, 0])
    # properAcceleration = np.array([-3.3141, -0.9338, -9.131])
    q, R = eCompass(properAcceleration, magneticFieldStrength)
    print(R)
    print(q)
    theta = -np.arcsin(R[0, 2])
    psi = np.arctan2(R[1, 2] / np.cos(theta), R[2, 2] / np.cos(theta))
    rho = np.arctan2(R[0, 1] / np.cos(theta), R[0, 0] / np.cos(theta))
    rotmatEulerAngles = np.rad2deg([rho, theta, psi])
    print(rotmatEulerAngles)
    # test 'quaternion' option
    print(q)
    q_R = quaternion.as_rotation_matrix(q)
    print(q_R)
    q_R[:, 2] *= 9.8
    theta = -np.arcsin(q_R[0, 2])
    psi = np.arctan2(q_R[1, 2] / np.cos(theta), q_R[2, 2] / np.cos(theta))
    rho = np.arctan2(q_R[0, 1] / np.cos(theta), q_R[0, 0] / np.cos(theta))
    qEulerAngles = np.rad2deg([rho, theta, psi])
    print(qEulerAngles)

    ## test th eGPT
    q_GPT, R_GPT = eCompassGPT(properAcceleration, magneticFieldStrength)
    print(q_GPT)
    print(R_GPT)

if __name__ == "__main__":
    # execute main
    main()



