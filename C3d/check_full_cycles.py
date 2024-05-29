import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json
import seaborn as sns

# load the df
activityName = "WalkShake"
metric = "StanceTime"
data = pd.read_csv('fullCyclesOptical.csv')
# data = data[data.Activity == activityName]
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
data.to_csv('fullCyclesOptical.csv', index=False)
print("Swing Time Violations\n************\n")
print(data[data["StrideTime"] < 0])
print(data[data["StrideTime"] > 150])
print("Stance Time Violations\n************\n")
print(data[data["StanceTime"] < 38])
# data[data["StanceTime"] > 82].to_csv('StanceTimeViolations.csv')
print(data[data["StanceTime"] < 38])

# check for no missed gait cycles
# data = data.groupby(["Subject", "TrialNum", "IC1"])
data["match"] = data.IC1.ne(data.IC3.shift(1)) & data.CycleSide.eq(data.CycleSide.shift(1))
print(data[data["match"] == True])
# data["match"] = data[data.IC1.eq(data.IC3.shift(1)) & data.CycleSide.eq(data.IC3.shift(1))]
# print(data.match)
# print(data.head(10))
