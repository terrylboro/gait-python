# This module contains the code for the 'Error Model' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 14/8/23

import numpy as np


def error_model(gAccel, magReadings, mGyro, g):
    """ Execute the 'Error Model' section of the AHRS algorithm
    Inputs:
    1x3 NP ARRAY gAccel
    N x 3 NP ARRAY FLOAT magReadings
    1x3 NP ARRAY mGyro
    1x3 NP ARRAY g
    Outputs:
    1x3 NP ARRAY z (error calculated)
    """

    # Diff between the gravity estimate from the accelerometer readings and the gyroscope readings
    # z_g = - (g - gAccel)
    z_g = gAccel - g
    # Diff between magnetic vector estimate from the gyroscope readings and magnetometer
    z_m = magReadings - mGyro
    # print(magReadings)
    # print(mGyro)
    # print("magVecMagGyroDiff: ", z_m)
    # z is simply a concatenation of the two
    z = np.concatenate((z_g, z_m), axis=0)
    return z

def main():
    gAccel = np.array([0.01, 0.005, 9.76])
    magReadings = np.array([0.07, 2.10, 28.3])
    mGyro = np.array([0.03, 2.25, 30.5])
    g = np.array([0, 0, 9.81])
    print(error_model(gAccel, magReadings, mGyro, g))


if __name__ == "__main__":
    # execute main
    main()
