import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R

from DefaultProperties import *


def compute_angular_velocity(gfast, offset):
    """Compute angular velocity by averaging gyroscope readings and subtracting bias (offset)."""
    gslow = np.sum(gfast, axis=0) / 1
    av = gslow - offset
    return av


def ecompass(accel, mag):
    """Compute the 3D orientation of a device from its accelerometer and magnetometer data."""
    down = -accel / np.linalg.norm(accel)
    east = np.cross(down, mag)
    east /= np.linalg.norm(east)
    north = np.cross(east, down)
    rot_matrix = np.vstack([north, east, down])
    rotation = R.from_matrix(rot_matrix)
    euler_angles = rotation.as_euler('zyx', degrees=True)
    return euler_angles


# Assumed values based on typical IMU Kalman filter implementations
# GyroscopeDriftNoise = np.zeros((1, 3))
# GyroscopeNoise = np.zeros()
# LinearAccelerationDecayFactor = 0.98
# LinearAccelerationNoise = np.zeros((1, 3))
pKalmanPeriod = 1 /200  # Assuming 1 time unit; this might need to be adjusted based on actual time steps in the data


def update_Q(Ppost):
    """Update the process noise covariance matrix Q based on Ppost and other parameters."""
    Q = np.zeros((10, 10))
    Q[:3, :3] = Ppost[:3, :3] + pKalmanPeriod ** 2 * (Ppost[3:6, 3:6] + GyroscopeDriftNoise + GyroscopeNoise)
    Q[3:6, 3:6] = Ppost[3:6, 3:6] + GyroscopeDriftNoise
    Q[6:9, 6:9] = (LinearAccelerationDecayFactor ** 2) * Ppost[6:9, 6:9] + LinearAccelerationNoise
    Q[:3, 3:6] = pKalmanPeriod * Ppost[:3, 3:6]
    Q[3:6, :3] = pKalmanPeriod * Ppost[3:6, :3]
    return Q

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
    print("hx: ", h)
    return h


def process_imu_data(file_path):
    """Load and process IMU data, returning the computed orientations."""

    # Load data
    imu_data = pd.read_csv(file_path)
    right_data = imu_data[
        ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'mag_x', 'mag_y', 'mag_z']].values

    # Pre-process data
    DecimationFactor = 1
    accelIn = right_data[:, :3].T.reshape(3, DecimationFactor, -1)
    gyroIn = right_data[:, 3:6].T.reshape(3, DecimationFactor, -1)
    accelIn = np.transpose(accelIn, (1, 0, 2))
    gyroIn = np.transpose(gyroIn, (1, 0, 2))
    numiters = accelIn.shape[2]


    # Kalman filter initialization
    initial_orientation = ecompass(accelIn[:, :, 0].flatten(), np.array([1, 0, 0]))
    initial_quaternion = R.from_euler('zyx', initial_orientation, degrees=True).as_quat()
    initial_state = np.hstack([initial_quaternion, [0, 0, 0], accelIn[:, :, 0].flatten()])
    Ppost = np.eye(10) * 0.01
    F = np.eye(10)

    # Kalman filter loop
    Xpost = initial_state
    orientations = []
    for iter in range(numiters):
        # Dynamically update Q
        Q = update_Q(Ppost)

        # 1. Prediction step
        Xpred = np.dot(F, Xpost)
        Ppred = np.dot(F, np.dot(Ppost, F.T)) + Q

        H = F
        accel_noise = AccelerometerNoise + LinearAccelerationNoise + pKalmanPeriod ** 2 * (GyroscopeDriftNoise + GyroscopeNoise)
        Qv = np.diag(np.array([accel_noise, accel_noise, accel_noise]))

        # 2. Update step
        S = np.dot(H, np.dot(Ppred, H.T)) + Qv
        K = np.dot(Ppred, np.dot(H.T, np.linalg.inv(S)))
        measurement = np.hstack([initial_quaternion, compute_angular_velocity(gyroIn[:, :, iter], np.zeros(3)),
                                 accelIn[:, :, iter].flatten()])
        # Y = measurement - np.dot(H, Xpred)
        # Xpost = Xpred + np.dot(K, Y)
        Xpost = measurement
        Ppost = Ppred - np.dot(K, np.dot(H, Ppred))
        orientations.append(R.from_quat(Xpost[:4]).as_euler('zyx', degrees=True))

    return orientations


if __name__ == "__main__":
    file_path = "/Data/Gimbal/gimbal-routine-try3.csv"  #input("Enter the path to your IMU data CSV file: ")
    orientations = process_imu_data(file_path)
    print("Processed orientations for the first 5 iterations:", orientations[:5])