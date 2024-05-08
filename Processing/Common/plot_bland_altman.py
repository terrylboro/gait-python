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

    plt.scatter(mean, diff, *args, **kwargs)
    plt.axhline(md,           color='gray', linestyle='--')
    plt.axhline(md + 1.96*sd, color='gray', linestyle='--')
    plt.axhline(md - 1.96*sd, color='gray', linestyle='--')


data = pd.read_csv('EarablesAdaptedDiaoComparison.csv')
print(data.head())
for metric in ["Stride Time", "Stance Time", "Swing Time"]:
    bland_altman_plot(data["Left {} Shank".format(metric)].to_numpy(), data["Left {} GT".format(metric)].to_numpy())
    plt.xlabel("Average of Earables and Optical Measurements")
    plt.ylabel("Difference between Earables and Optical Measurements")
    plt.title("{} Comparison of Earables and Optical Systems".format(metric))
    plt.show()
