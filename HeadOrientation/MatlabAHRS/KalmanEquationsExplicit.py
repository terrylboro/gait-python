# This module contains the code for the 'Kalman Filter' section of the Matlab AHRS algorithm
# This is the version written without library dependencies, for the filterpy implementation
# see KalmanEquations.py
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 20/8/23

import numpy as np
from DefaultProperties import *


def kalman_forward(g, mGyro, ze, is6axis, pQw):
    """ Execute the kalman equations """
    # Qv or R is the covariance of the observation model noise
    k = DecimationFactor / SampleRate
    accel_noise = AccelerometerNoise + LinearAccelerationNoise + k ** 2 * (GyroscopeDriftNoise + GyroscopeNoise)
    mag_noise = MagnetometerNoise + MagneticDisturbanceNoise + k ** 2 * (GyroscopeDriftNoise + GyroscopeNoise)

    if is6axis:
        Qv = np.diag(np.array([accel_noise, accel_noise, accel_noise]))
        Qw = pQw
        # Compute the observation model (H) matrix
        H = compute_h_6axis(g, k)
        # print("H: ", H)
    else:
        Qv = np.diag(np.array([accel_noise, accel_noise, accel_noise, mag_noise, mag_noise, mag_noise]))
        # Qw is the process noise (also referred to as p-)
        Qw = pQw
        # Qw = np.diag(np.array([0.000006092348396, 0.000006092348396, 0.000006092348396,
        #           0.000076154354947, 0.000076154354947, 0.000076154354947,
        #           0.009623610000000, 0.009623610000000, 0.009623610000000,
        #           0.600000000000000, 0.600000000000000, 0.600000000000000]))
        # Compute the observation model (H) matrix
        H = compute_h(g, mGyro, k)
        # print("H: ", H)
    # innovation covariance, S aka tmp
    S = compute_s(H, Qw, Qv)
    # print("tmp: ", S)
    # Calculate the Kalman gain, K_12x6
    K = compute_K(Qw, H, S)
    # print("K: ", K)
    xe_post = np.matmul(K, ze)
    # print("xe_post: ", xe_post)
    if is6axis:
        update_Qw_6axis(Qw, K, H, GyroscopeDriftNoise, GyroscopeNoise, LinearAccelerationDecayFactor, LinearAccelerationNoise, (DecimationFactor/SampleRate))
    else:
        update_Qw_9axis(Qw, K, H, GyroscopeDriftNoise, GyroscopeNoise, LinearAccelerationDecayFactor,
                        LinearAccelerationNoise, MagneticDisturbanceDecayFactor, MagneticDisturbanceNoise, (DecimationFactor/SampleRate))
    # print(xe_post)
    return xe_post, K, Qw


def update_Qw_6axis(Qw, K, H, beta, epsilon, nu, xi, k):
    p = calculate_pplus(Qw, K, H)
    # print("pplus: ", p)
    Qw[0, 0] = p[0, 0] + k ** 2 * (p[3, 3] + beta + epsilon)
    Qw[3, 0] = -k * (p[3, 3] + beta)
    Qw[1, 1] = p[1, 1] + k ** 2 * (p[4, 4] + beta + epsilon)
    Qw[4, 1] = -k * (p[4, 4] + beta)
    Qw[2, 2] = p[2, 2] + k ** 2 * (p[5, 5] + beta + epsilon)
    Qw[5, 2] = -k * (p[5, 5] + beta)
    Qw[0, 3] = -k * (p[3, 3] + beta)
    Qw[3, 3] = p[3, 3] + beta
    Qw[1, 4] = -k * (p[4, 4] + beta)
    Qw[4, 4] = p[4, 4] + beta
    Qw[2, 5] = -k * (p[5, 5] + beta)
    Qw[5, 5] = p[5, 5] + beta
    # onto the accelerometer section
    Qw[6, 6] = nu ** 2 * p[6, 6] + xi
    Qw[7, 7] = nu ** 2 * p[7, 7] + xi
    Qw[8, 8] = nu ** 2 * p[8, 8] + xi


def update_Qw_9axis(Qw, K, H, beta, epsilon, nu, xi, sigma, gamma, k):
    p = calculate_pplus(Qw, K, H)
    # print("pplus: ", p)
    Qw[0, 0] = p[0, 0] + k ** 2 * (p[3, 3] + beta + epsilon)
    Qw[3, 0] = -k * (p[3, 3] + beta)
    Qw[1, 1] = p[1, 1] + k ** 2 * (p[4, 4] + beta + epsilon)
    Qw[4, 1] = -k * (p[4, 4] + beta)
    Qw[2, 2] = p[2, 2] + k ** 2 * (p[5, 5] + beta + epsilon)
    Qw[5, 2] = -k * (p[5, 5] + beta)
    Qw[0, 3] = -k * (p[3, 3] + beta)
    Qw[3, 3] = p[3, 3] + beta
    Qw[1, 4] = -k * (p[4, 4] + beta)
    Qw[4, 4] = p[4, 4] + beta
    Qw[2, 5] = -k * (p[5, 5] + beta)
    Qw[5, 5] = p[5, 5] + beta
    # onto the accelerometer section
    Qw[6, 6] = nu ** 2 * p[6, 6] + xi
    Qw[7, 7] = nu ** 2 * p[7, 7] + xi
    Qw[8, 8] = nu ** 2 * p[8, 8] + xi
    # mag
    Qw[9, 9] = sigma ** 2 * p[9, 9] + gamma
    Qw[10, 10] = sigma ** 2 * p[10, 10] + gamma
    Qw[11, 11] = sigma ** 2 * p[11, 11] + gamma


def calculate_pplus(Qw, K, H):
    pplus = Qw - np.matmul(K, (np.matmul(H, Qw)))
    return pplus


def compute_h(g, mGyro, k):
    """ Compute the measurement matrix, H """
    h1 = build_h_part(g)
    h2 = build_h_part(mGyro)
    h3 = -h1 * k
    h4 = -h2 * k
    top_H = np.concatenate((np.array(h1), np.array(h3), np.identity(3), np.zeros((3, 3))), axis=1)
    bottom_H = np.concatenate((np.array(h2), np.array(h4), np.zeros((3,3)), -1 * np.identity(3)), axis=1)
    H = np.vstack((top_H, bottom_H))
    H = np.reshape(H, (6, 12))
    return H

def compute_h_6axis(g, k):
    """ Compute the measurement matrix, H3x9, only using g  """
    h1 = build_h_part(g)
    h3 = -h1 * k
    H = np.concatenate((np.array(h1), np.array(h3), np.identity(3)), axis=1)
    return H


def build_h_part(v):
    """ Build a portion of the H matrix """
    h = np.zeros((3, 3))
    h[0, 1] = v[2]
    h[0, 2] = -v[1]
    h[1, 2] = v[0]
    h = h - h.T
    # print("hx: ", h)
    return h


def compute_s(H, Qw, Qv):
    S = (np.matmul(np.matmul(H, Qw), H.T) + Qv).T
    return S


def compute_K(Qw, H, S):
    K = np.matmul(np.matmul(Qw, H.T), np.linalg.inv(S))
    return K

def quaternion_multiply(Q1, Q2):
    # 0, 1, 2, 3
    # 3, 0, 1, 2

    w = Q1[3] * Q2[3] - Q1[0] * Q2[0] - Q1[1] * Q2[1] - Q1[2] * Q2[2]
    x = Q1[3] * Q2[0] + Q1[0] * Q2[3] + Q1[1] * Q2[2] - Q1[2] * Q2[1]
    y = Q1[3] * Q2[1] - Q1[0] * Q2[2] + Q1[1] * Q2[3] + Q1[2] * Q2[0]
    z = Q1[3] * Q2[2] + Q1[0] * Q2[1] - Q1[1] * Q2[0] + Q1[2] * Q2[3]
    return np.array([x, y, z, w])


def main():
    mGyro = np.array([-152.75551914, - 0.86885065,  413.69795811])
    g = np.array([3.39460768,  0.01778803, -9.19327593])
    ze = np.array([6.76993088, -1.05037908, -18.30071331, -138.84474813, 1.0252495, 499.51620571])
    kalman_forward(g, mGyro, ze)

if __name__ == "__main__":
    # execute main
    main()

