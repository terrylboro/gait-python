# This module contains the default filter parameters for the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 15/8/23

import numpy as np

SampleRate = 200
DecimationFactor = 1
AccelerometerNoise = 0.00019247 # Variance of accelerometer signal noise ((m/s2)2)
MagnetometerNoise = 0.1 # Variance of magnetometer signal noise (μT2)
GyroscopeNoise = 9.1385 * 10**-5 # Variance of gyroscope signal noise ((rad/s)2)
GyroscopeDriftNoise = 3.0462 * 10**-13 # Variance of gyroscope offset drift ((rad/s)2)
LinearAccelerationNoise = 0.0096236 # Variance of linear acceleration noise (m/s2)2
LinearAccelerationDecayFactor = 0.5 # Decay factor for linear drift, range [0,1]. Set low if linear accel. changes quickly
MagneticDisturbanceNoise = 0.5 # Variance of magnetic disturbance noise (μT2)
MagneticDisturbanceDecayFactor = 0.5 # Decay factor for magnetic disturbance
InitialProcessNoise = np.array([0.000006092348396, 0.000006092348396, 0.000006092348396,
                                0.000076154354947, 0.000076154354947, 0.000076154354947,
                                0.009623610000000, 0.009623610000000, 0.009623610000000,
                                0.600000000000000, 0.600000000000000, 0.600000000000000]) * np.identity(12)
ExpectedMagneticFieldStrength = 50 #  Expected estimate of magnetic field strength (μT)
OrientationFormat = 'quaternion' # can switch to 'Rotation matrix