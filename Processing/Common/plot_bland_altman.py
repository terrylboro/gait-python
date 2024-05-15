import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def bland_altman_plot(data1, data2, *args, **kwargs):
    # data1     = np.asarray(data1)
    # data2     = np.asarray(data2)
    # print(data1)
    mean      = np.nanmean([data1, data2], axis=0)
    diff      = data1 - data2                   # Difference between data1 and data2
    md        = np.nanmean(diff)                   # Mean of the difference
    sd        = np.nanstd(diff, axis=0)            # Standard deviation of the difference


    # print(diff[np.where(abs(diff[:] > 20))])
    # print(np.where(abs(diff > 20)))
    plt.scatter(mean, diff, *args, **kwargs)
    plt.axhline(md,           color='gray', linestyle='--')
    plt.axhline(md + 1.96*sd, color='gray', linestyle='--')
    plt.axhline(md - 1.96*sd, color='gray', linestyle='--')


# data = pd.read_csv('../Ear/Events/AdaptedDiao/Comparison/EarAdaptedDiaoComparison.csv')
# data = pd.read_csv('../Shank/Events/Gyro/Comparison/ShankGyroComparison.csv')
data = pd.read_csv('../Chest/Events/McCamley/Comparison/ChestMcCamleyComparison.csv')
print(data.head())
for metric in ["Stride Time", "Stance Time", "Swing Time"]:
    bland_altman_plot(data["Left {} Shank".format(metric)].to_numpy(), data["Left {} GT".format(metric)].to_numpy())
    plt.xlabel("Average of Ear IMU and Optical Measurements")
    plt.ylabel("Difference between Ear IMU and Optical Measurements")
    plt.title("{} Comparison of Ear IMU and Optical Systems".format(metric))
    plt.show()
    plt.savefig(metric + " Comparison of Ear IMU and Optical Measurements.png", dpi=100)
    plt.clf()
