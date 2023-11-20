# This module contains the code for the 'Update Magnetic Vector' section of the Matlab AHRS algorithm
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 16/8/23
import numpy as np
import MyQuaternionFunctions
from DefaultProperties import ExpectedMagneticFieldStrength


def update_magnetic_vector(q_plus, mError, old_m):
    """ If magnetic jamming was not detected in the current iteration, the magnetic vector estimate, m, is updated
    using the a posteriori magnetic disturbance error and the a posteriori orientation.
    """
    rPost = MyQuaternionFunctions.quaternion_rotation_matrix(q_plus)
    mErrorNED = np.matmul(rPost.T, mError.T).T
    old_m = np.reshape(old_m, 3)
    # The magnetic disturbance error in the navigation frame is subtracted from the previous magnetic vector estimate and then interpreted as inclination:
    M = old_m - mErrorNED
    inclination = np.arctan2(M[2], M[0])
    # The inclination is converted to a constrained magnetic vector estimate for the next iteration:
    m = np.zeros((1, 3))
    m[0, 0] = ExpectedMagneticFieldStrength * np.cos(inclination)
    m[0, 2] = ExpectedMagneticFieldStrength * np.sin(inclination)
    return m


def main():
    # q_plus = quaternion.as_quat_array([[1, 19.535, -5.109, 47.930]])
    # mError = np.empty((1, 3))
    # old_m = np.empty((1, 3))
    # mError[0:3] = [3.5, -1.5, 5.2]
    # old_m[0:3] = [16.535, -2.109, 51.930]
    # m = update_magnetic_vector(q_plus, mError, old_m)
    print("Hi")


if __name__ == "__main__":
    # execute main
    main()
