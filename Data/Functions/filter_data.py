import numpy as np
import pandas as pd
from scipy import signal, integrate
import matplotlib.pyplot as plt


def filter_data(data):
    """
    Apply the preprocessing steps
    :param data:
    :return: Preprocessed data
    """
    # data = signal.detrend(data)
    means = np.mean(data, axis=0)
    data = data - means
    sos = signal.butter(2, 25, btype="low", fs=100, output='sos')
    filtered_data = signal.sosfilt(sos, data)
    # plt.figure()
    # plt.plot(filtered_data)
    filtered_data = filtered_data + means
    # plt.figure()
    # plt.plot(filtered_data)
    # plt.show()
    processed_data = integrate.cumulative_trapezoid(filtered_data)
    return filtered_data, processed_data


