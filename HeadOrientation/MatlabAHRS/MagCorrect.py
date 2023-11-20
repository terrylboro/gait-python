# This module contains the code for the 'Magnetometer Correct' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 16/8/23

import numpy as np
from DefaultProperties import ExpectedMagneticFieldStrength


def magnetometer_correct(z, k):
    """ Estimate error in magnetic vector estimate and detect magnetic jamming
    Inputs:
    z -- np.array(1x6) error vector
    K -- np.array(3x6) last 3 rows of Kalman gain (associated with magnetic vector error) 
    Outputs:
    mError -- np.array(3x1) magnetic disturbance error
    tf -- bool indicating magnetic jamming"""
    mError = np.matmul(k, z.T).T
    # magnetic jamming is detected if the magnetic disturbance magnitude squared is <= 4 * power of expected field strength
    if np.sum(mError.dot(mError.T)) > 4 * ExpectedMagneticFieldStrength ** 2:
        tf = True
    else:
        tf = False
    return mError, tf


def main():
    z = np.array([0.02, 0.5, 0.12, 0.55, 0.23, 0.01])
    k = np.random.random_sample((3, 6))
    mError, tf = magnetometer_correct(z, k)
    print(mError)
    print(tf)


if __name__ == "__main__":
    # execute main
    main()
