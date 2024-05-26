import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json

# load the df
data = pd.read_csv('fullCyclesOptical.csv')
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
print(data[data["StrideTime"] < minStrideTime])
print(data[data["StrideTime"] > maxStrideTime])
print("Stance Time Violations\n************\n")
print(data[data["StanceTime"] > 75])
print(data[data["StanceTime"] < 45])
