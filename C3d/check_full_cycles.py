import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json
import seaborn as sns

# load the df
activityName = "Walk"
metric = "StanceTime"
data = pd.read_csv('fullCyclesOptical.csv')
data = data[data.Activity == activityName]
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
ax1 = data[data["Subject"].isin(range(1, 10))].plot.scatter(x="Subject",y=metric,
                                                             c="TrialNum", colormap="viridis")
# g = sns.relplot(data=data[data["Subject"].isin(range(1, 68))], x='Subject', y=metric, hue='Condition',
#             hue_order=["Typical", "Parkinsons", "Comorbities", "Balance"])
# leg = g._legend
# leg.set_bbox_to_anchor([0.4, 0.75])  # coordinates of lower left of bounding box
plt.title("{} {} data for all participants".format(activityName, metric))
# plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

# # Violin Plotting
# fig, axes = plt.subplots()
# # sns.violinplot(x=data["Subject"], y=data[metric], ax = axes)
# sns.violinplot(data=data[data["Subject"].isin(range(5, 7))], x="Subject", y=metric, hue="TrialNum")
# axes.set_title('Violin Plot for {}'.format(activityName))
# axes.yaxis.grid(True)
# axes.set_xlabel('Participant')
# axes.set_ylabel(metric)
# plt.show()
