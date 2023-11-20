# A class which implements the Matlab AHRS filter algorithm in Python
# https://uk.mathworks.com/help/fusion/ref/ahrsfilter-system-object.html
# Written by Terry Fawden 16/8/23

# import functions from the submodules
import Model, Correct, MagCorrect, ErrorModel, KalmanEquations, DefaultProperties, ComputeAngularVelocity, UpdateMagneticVector, ECompass, KalmanEquationsExplicit
import numpy as np
import pandas as pd
from plotData import plot_imu_xyz, plot_euler_angles
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
import os
from quat_to_euler import quat_array_to_euler


class AHRS:
    """ A Python implementation of the Matlab AHRS filter """
    def __init__(self, accelReadings, gyroReadings, magReadings):
        """ Setup the default properties of the filter and input arrays
        \nInputs:
        accelReadings -- np.array(Nx3) float in m/s^2\n
        gyroReadings -- np.array(Nx3) float in rad/s\n
        magReadings -- np.array(Nx3) float in uT """
        # set the default properties of the filter
        self.SampleRate = 200
        self.DecimationFactor = 1
        self.AccelerometerNoise = 0.00019247  # Variance of accelerometer signal noise ((m/s2)2)
        self.MagnetometerNoise = 0.1  # Variance of magnetometer signal noise (μT2)
        self.GyroscopeNoise = 9.1385 * 10 ** -5  # Variance of gyroscope signal noise ((rad/s)2)
        self.GyroscopeDriftNoise = 3.0462 * 10 ** -13  # Variance of gyroscope offset drift ((rad/s)2)
        self.LinearAccelerationNoise = 0.0096236  # Variance of linear acceleration noise (m/s2)2
        self.LinearAccelerationDecayFactor = 0.5  # Decay factor for linear drift, range [0,1]. Set low if linear accel. changes quickly
        self.MagneticDisturbanceNoise = 0.5  # Variance of magnetic disturbance noise (μT2)
        self.MagneticDisturbanceDecayFactor = 0.5  # Decay factor for magnetic disturbance
        self.InitialProcessNoise = np.array([0.000006092348396, 0.000006092348396, 0.000006092348396,
                                        0.000076154354947, 0.000076154354947, 0.000076154354947,
                                        0.009623610000000, 0.009623610000000, 0.009623610000000,
                                        0.600000000000000, 0.600000000000000, 0.600000000000000]) * np.identity(12)
        self.ExpectedMagneticFieldStrength = 50  # Expected estimate of magnetic field strength (μT)
        self.OrientationFormat = 'quaternion'  # can switch to 'Rotation matrix
        # Array size constants
        self.N = np.size(accelReadings, 0)
        self.M = int(self.N / self.DecimationFactor)
        # assign the IMU data
        self.accelReadings = accelReadings
        self.gyroReadings = gyroReadings
        self.magReadings = magReadings
        # setup output variables
        self.orientation = np.zeros((self.M, 4)) #   quaternion.as_quat_array(orientation_np_array)
        self.orientation_euler = np.zeros((self.M, 3))
        self.angularVelocity = np.zeros((self.M, 3))
        self.rotmat = np.zeros((self.M, 9))
        # initialise internal state variables for first pass
        self.isFirst = True
        self.linAccelPrior = np.zeros(3)  # assume stationary start
        # self.gyroOffset = np.array([-0.01, 0, 0.01])  # set this according to pre calibration
        # if os.path.isfile("C:/Users/teri-/PycharmProjects/headinspace/Data/Calibration/right-offsets.txt"):
        #     self.gyroOffset = np.loadtxt("C:/Users/teri-/PycharmProjects/headinspace/Data/Calibration/right-offsets.txt", delimiter=',')
        # else:
        self.gyroOffset = np.zeros(3)  # set this according to pre calibration
        print("gyroOffset: ", self.gyroOffset)
        self.q_plus, self.Q_plus_rot_Mat = ECompass.eCompassGPT(accelReadings[0, :], magReadings[0, :])
        print("pOrientPost: ", self.q_plus)
        self.m = self.ExpectedMagneticFieldStrength * np.array([1, 0, 0])
        # initialise noise variances
        self.Qw = np.diag(np.array([0.000006092348396, 0.000006092348396, 0.000006092348396,
                               0.000076154354947, 0.000076154354947, 0.000076154354947,
                               0.009623610000000, 0.009623610000000, 0.00962361000000,
                                0.600000000000000, 0.600000000000000, 0.600000000000000]))

    def run(self, savedir, filename):
        """ Apply the filtering algorithm """
        # q_plus is initialised using eCompass during first pass
        # linAccelPrior can surely be initialised as zero - impose 'standing still' start condition. Not mentioned on website.
        # initial gyro offset can be determined beforehand using calibration. It should adapt throughout anyway.
        # for i in range(0, 2):
        for i in range(0, self.M):
            self.angularVelocity[i] = ComputeAngularVelocity.compute_angular_velocity(self.gyroReadings[i, :], self.gyroOffset)
            self.gAccel, self.mGyro, self.g, self.q_minus, self.linAccelPrior = Model.model(self.accelReadings[i, :], self.gyroReadings[i, :], self.magReadings[i, :], self.gyroOffset, self.linAccelPrior, self.m, self.q_plus, i)
            # print("linAccelPrior: ", self.linAccelPrior)
            # print("mGyro: ", self.mGyro)
            # print("q_minus", self.q_minus)
            self.z = ErrorModel.error_model(self.gAccel, self.magReadings[i, :], self.mGyro, self.g)
            # print("z: ", self.z)
            # apply the Kalman Equations here
            self.x, self.K, self.Qw = KalmanEquationsExplicit.kalman_forward(self.g, self.mGyro, self.z, False, self.Qw)
            # print("K: ", self.K)
            # print("x: ", self.x)
            self.mError, self.tf = MagCorrect.magnetometer_correct(self.z, self.K[9:12])
            # print("magDistErr: ", self.mError)
            self.q_plus, self.linAccelPrior, self.gyroOffset = Correct.correct(self.x, self.q_minus,
                                                                               self.linAccelPrior, self.gyroOffset)
            # print("pLinAccelPost: ", self.linAccelPrior)
            #

            # self.mError, self.tf = MagCorrect.magnetometer_correct(self.z, kalEqns.f.K[9:12])
            # self.q_plus, self.linAccelPrior, self.gyroOffset = Correct.correct(kalEqns.f.x, self.q_minus, self.linAccelPrior, self.gyroOffset)
            self.m = UpdateMagneticVector.update_magnetic_vector(self.q_plus, self.mError, self.m)
            # print("pMagVec: ", self.m)
            # Append orientation quaternion to list
            self.orientation[i] = self.q_plus
            self.orientation_euler[i] = R.from_quat(self.q_plus).as_euler('zyx', degrees=True)
            self.rotmat[i] = R.from_quat(self.q_plus).as_matrix().flatten()
        # save orientation to CSV file
        np.savetxt(savedir + filename + "-quaternion" + ".csv", self.orientation, delimiter=",", fmt="%.16f")
        self.orientation_euler = quat_array_to_euler(self.orientation)
        np.savetxt(savedir + filename + "-euler" + ".csv", self.orientation_euler, delimiter=",", fmt="%.16f")
        np.savetxt(savedir + filename + "-rotmat" + ".csv", self.rotmat, delimiter=",", fmt="%.16f")
        # plot findings
        plot_imu_xyz(self.accelReadings, self.gyroReadings, self.magReadings, range(0, len(self.accelReadings)),
                     "NED IMU Data", 1)
        plot_euler_angles(range(0, len(self.accelReadings)), self.orientation_euler,
                          filename, 2)
        # plt.show()

    def run_6axis(self, savedir):
        self.gaccel_array = np.zeros((self.M, 3))
        for i in range(0, self.M):
            self.angularVelocity[i] = ComputeAngularVelocity.compute_angular_velocity(self.gyroReadings[i, :], self.gyroOffset)
            self.gAccel, self.mGyro, self.g, self.q_minus, self.linAccelPrior = Model.model(self.accelReadings[i, :], self.gyroReadings[i, :], self.magReadings[i, :], self.gyroOffset, self.linAccelPrior, self.m, self.q_plus, i)
            self.z = ErrorModel.error_model(self.gAccel, self.magReadings[i, :], self.mGyro, self.g)
            self.z = self.z[0:3]  # only keep track of accel and gyro
            # print("ze: ", self.z)
            self.x, self.K, self.Qw = KalmanEquationsExplicit.kalman_forward(self.g, self.mGyro, self.z, True, self.Qw)
            # print("x is: ", self.x)
            self.q_plus, self.linAccelPrior, self.gyroOffset = Correct.correct(self.x, self.q_minus,
                                                                               self.linAccelPrior, self.gyroOffset)
            # Append orientation quaternion to list
            self.orientation[i] = self.q_plus
            self.orientation_euler[i] = R.from_quat(self.q_plus).as_euler('zyx', degrees=True)
            self.gaccel_array[i] = self.gAccel
        plot_imu_xyz(self.accelReadings, self.gyroReadings, self.magReadings, range(0, len(self.accelReadings)),
                     "Input Data", 1)
        plot_euler_angles(range(0, len(self.accelReadings)), self.orientation_euler,
                          "Euler Angles (Python)", 2)
        plt.show()


def main():
    subject = "TF_00"
    side = "Left"
    loaddir = "../Data/" + subject + "/Walk/Readings/" + side + "/"
    savedir = "../Data/" + subject + "/Walk/Angles/" + side + "/"
    # trialname = "TF_00-02_NED_left.csv"
    for file in os.listdir(loaddir):
        # if file == trialname:
        data = pd.read_csv(loaddir + file)
        print(data)
        accel = data[['AccX', 'AccY', 'AccZ']].values
        gyro = data[['GyroX', 'GyroY', 'GyroZ']].values
        mag = data[['MagX', 'MagY', 'MagZ']].values
        N = np.size(accel, 0)
        # Rearrange the data to fit the correct format
        accelReadings = np.reshape(accel[:, :], (N, 3))
        gyroReadings = np.reshape(gyro[:, :], (N, 3))
        magReadings = np.reshape(mag[:, :], (N, 3))

        ahrs = AHRS(accelReadings, gyroReadings, magReadings)
        # ahrs.run_6axis(savedir, file.split(".")[0])
        ahrs.run(savedir, file.split(".")[0] + "-" + side)


if __name__ == "__main__":
    main()


