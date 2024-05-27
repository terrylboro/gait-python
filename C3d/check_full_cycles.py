import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json

# load the df
data = pd.read_csv('fullCyclesOptical.csv')
data = data[data.Activity == "WalkShake"]
# print(data.head())

# set our limits
minStrideTime = 70
maxStrideTime = 225
minStrideDutyCycle = 0.44
maxStrideDutyCycle = 0.73

# Calculate stride times
data["StrideTime"] = data["IC3"] - data["IC1"]
data["StanceTime"] = data["FO2"] - data["IC1"]
data["SwingTime"] = data["IC3"] - data["FO2"]
print("Swing Time Violations\n************\n")
print(data[data["StrideTime"] < 0])
print(data[data["StrideTime"] > 150])
print("Stance Time Violations\n************\n")
print(data[data["StanceTime"] < 38])
# data[data["StanceTime"] > 82].to_csv('StanceTimeViolations.csv')
print(data[data["StanceTime"] < 38])

# plot the data for all participants
ax1 = data[data["Subject"].isin(range(42, 43))].plot.scatter(x="Subject",y="StanceTime",
                                                             c="TrialNum", colormap="viridis")
plt.show()
