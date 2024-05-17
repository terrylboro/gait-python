import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def bland_altman_plot(data1, data2, color, *args, **kwargs):
    # data1     = np.asarray(data1)
    # data2     = np.asarray(data2)
    # print(data1)
    mean      = np.nanmean([data1, data2], axis=0)
    diff      = data1 - data2                   # Difference between data1 and data2
    md        = np.nanmean(diff)                   # Mean of the difference
    sd        = np.nanstd(diff, axis=0)            # Standard deviation of the difference


    plt.scatter(mean, diff, *args, **kwargs)
    plt.axhline(md,           color=color, linestyle='--')
    plt.axhline(md + 1.96*sd, color=color, linestyle='--')
    plt.axhline(md - 1.96*sd, color=color, linestyle='--')

location = "Shank"
# data = pd.read_csv('../Ear/Events/AdaptedDiao/Comparison/EarAdaptedDiaoComparison.csv')
data = pd.read_csv('../Shank/Events/Gyro/Comparison/ShankGyroComparison.csv')
# data = pd.read_csv('../Chest/Events/McCamley/Comparison/ChestMcCamleyComparison.csv')
print(data.head())
NTFs = [30, 31, 36, 42, 43, 44, 45, 55, 56, 66, 67]
for metric in ["Stride Time", "Stance Time", "Swing Time"]:
    tfData = data[data.Subject.isin(NTFs)]
    ntfData = data[~data.Subject.isin(NTFs)]
    # print(ntfData)
    bland_altman_plot(data["Left {} Shank".format(metric)].to_numpy(), data["Left {} GT".format(metric)].to_numpy(), "blue")
    bland_altman_plot(ntfData["Left {} Shank".format(metric)].to_numpy(), ntfData["Left {} GT".format(metric)].to_numpy(), "orange")
    plt.xlabel("Average of {} IMU and Optical Measurements".format(location))
    plt.ylabel("Difference between {} IMU and Optical Measurements".format(location))
    plt.title("{} Comparison of {} IMU and Optical Systems".format(metric, location))
    # plt.show()
    plt.savefig(metric + " Comparison of {} IMU and Optical Measurements.png".format(location), dpi=100)
    plt.clf()
