# This module contains the code for the 'Kalman Filter' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 15/8/23

import numpy as np
from filterpy.kalman import KalmanFilter
from DefaultProperties import *


class KalmanEquations:
    def __init__(self, mGyro, g):
        """ Setup and execute the kalman filter """
        self.f = KalmanFilter(dim_x=12, dim_z=6)
        # Because x_k is defined as the error process, the a priori estimate is always zero
        # f.x = 0 [we can comment out as this is the default]
        # and therefore the state transition model, Fk, is zero
        # self.f.F = 0
        self.k = DecimationFactor / SampleRate  # this is DecimationFactor / SampleRate
        # set observation model / measurement matrix, H [true state, 6x12]
        temp_H = [0, g[2], -g[1], 0, -self.k * g[2], self.k * g[1], 1, 0, 0, 0, 0, 0,
                       -g[2], 0, g[0], self.k * g[2], 0, -self.k * g[0], 0, 1, 0, 0, 0, 0,
                       g[1], -g[0], 0, -self.k * g[1], self.k * g[0], 0, 0, 0, 1, 0, 0, 0,
                       0, mGyro[2], -mGyro[1], 0, -self.k * mGyro[2], -self.k * mGyro[1], 0, 0, 0, -1, 0, 0,
                       -mGyro[2], 0, mGyro[0], self.k * mGyro[2], 0, -self.k * mGyro[0], 0, 0, 0, 0, -1, 0,
                       mGyro[1], -mGyro[0], 0, -self.k * mGyro[1], self.k * mGyro[0], 0, 0, 0, 0, 0, 0, -1]
        self.f.H = np.reshape(temp_H, (6, 12))
        # I believe p is not defined for the first iteration, so we'll leave it as default
        # R is covariance matrix of observation model noise [measurement uncertainty/noise]
        self.accel_noise = AccelerometerNoise + LinearAccelerationNoise +self.k ** 2 * (GyroscopeDriftNoise + GyroscopeNoise)
        self.mag_noise = MagnetometerNoise + MagneticDisturbanceNoise +self.k ** 2 * (GyroscopeDriftNoise + GyroscopeNoise)
        self.f.R = np.diag(np.array([self.accel_noise, self.accel_noise, self.accel_noise, self.mag_noise, self.mag_noise, self.mag_noise]))
        # print(self.f.R)
        # Q appears to have a default setting
        self.f.Q = InitialProcessNoise

    def run(self, z):
        """ Execute the Kalman Filtering operations for a single pass """
        self.f.predict()
        self.f.update(z)
        # Noise covariance, Q is calculated as a function of a posteriori error est. cov., p_+
        # Assumes that cross-correlation terms are neglibible vs autocorrelation terms
        # we update this prior to executing the prediction step
        self.set_Q(GyroscopeDriftNoise, GyroscopeNoise, LinearAccelerationDecayFactor, LinearAccelerationNoise, MagneticDisturbanceDecayFactor, MagneticDisturbanceNoise)

    def set_Q(self, beta, epsilon, nu, xi, sigma, gamma):
        """ Predict the error covariance matrix, Q
        self.f -- the Kalman Filter object
        self.k -- DecimationFactor / SampleRate
        β –– GyroscopeDriftNoise
        η –– GyroscopeNoise
        ν –– LinearAccelerationDecayFactor
        ξ –– LinearAccelerationNoise
        σ –– MagneticDisturbanceDecayFactor
        γ –– MagneticDisturbanceNoise """
        Q = np.zeros([12, 12])
        p = self.f.P  # p+
        # populate column-by-column, see
        # https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html#mw_8905f4e8-b103-4c91-a7fd-e2baea5325b8
        Q[0, 0] = p[0, 0] + self.k ** 2 * (p[3, 3] + beta + epsilon)
        Q[3, 0] = -self.k * (p[3, 3] + beta)
        Q[1, 1] = p[1, 1] + self.k ** 2 * (p[4, 4] + beta + epsilon)
        Q[4, 1] = -self.k * (p[4, 4] + beta)
        Q[2, 2] = p[2, 2] + self.k ** 2 * (p[5, 5] + beta + epsilon)
        Q[5, 2] = -self.k * (p[5, 5] + beta)
        Q[0, 3] = -self.k * (p[0, 3] + beta)
        Q[3, 3] = p[3, 3] + beta
        Q[1, 4] = -self.k * (p[1, 4] + beta)
        Q[4, 4] = p[4, 4] + beta
        Q[2, 5] = -self.k * (p[2, 5] + beta)
        Q[5, 5] = p[5, 5] + beta
        # onto the accelerometer section
        Q[6, 6] = nu ** 2 * p[6, 6] + xi
        Q[7, 7] = nu ** 2 * p[7, 7] + xi
        Q[8, 8] = nu ** 2 * p[8, 8] + xi
        # magnetometer section
        Q[9, 9] = sigma ** 2 * p[9, 9] + gamma
        Q[10, 10] = sigma ** 2 * p[10, 10] + gamma
        Q[11, 11] = sigma ** 2 * p[11, 11] + gamma
        self.f.Q = Q


def main():
    mGyro = np.array([0.03, 2.25, 30.5])
    g = np.array([0, 0, 9.81])
    z = np.array([0.02, 0.5, 0.12, 0.55, 0.23, 0.01])
    k = KalmanEquations(mGyro, g)
    k.run(z)
    print(k.f.x)

if __name__ == "__main__":
    # execute main
    main()
