# This module contains the code for the 'Compute Angular Velocity' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 16/8/23
import numpy as np
from DefaultProperties import DecimationFactor


def compute_angular_velocity(gyroReadings, gyroOffset):
    """ To estimate angular velocity, the frame of gyroReadings are averaged
    and the gyroscope offset computed in the previous iteration is subtracted:"""
    if gyroReadings.ndim > 1:
        angularVelocity = np.sum(gyroReadings, axis=1) / DecimationFactor - gyroOffset
    else:
        angularVelocity = gyroReadings / DecimationFactor - gyroOffset
    return angularVelocity
