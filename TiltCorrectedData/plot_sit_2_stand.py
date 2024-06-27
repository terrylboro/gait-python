import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from textwrap import wrap

# define the fps
typicalFP = "TF_59/Sit2Stand/Left/TF_59-31_NED.csv"
nonTypicalFP = "TF_55/Sit2Stand/Left/TF_55-25_NED.csv"

# load the data
typicalDF = pd.read_csv(typicalFP, usecols=["AccX", "AccY", "AccZ"])
nonTypicalDF = pd.read_csv(nonTypicalFP, usecols=["AccX", "AccY", "AccZ"])


fig, axes = plt.subplots(3, 2, figsize=(15, 5), sharex=True)
fig.suptitle('Sit-to-Stand IMU Comparison Between Young Participant and Participant with Parkinson\'s',
             fontsize='xx-large')
xtypical = np.linspace(0, len(typicalDF)/100, len(typicalDF))
xnontypical = np.linspace(0, len(nonTypicalDF)/100, len(nonTypicalDF))
# Healthy
g = sns.lineplot(ax=axes[0, 0], x=xtypical, y=typicalDF.AccX, color='g')
axes[0, 0].set_title("Young Participant", fontsize='x-large')
axes[0, 0].set_ylabel("AccX", fontsize='large')
axes[0, 0].yaxis.set_label_coords(-0.07,0.5)
sns.lineplot(ax=axes[1, 0], x=xtypical, y=typicalDF.AccY, color='r')
axes[1, 0].set_ylabel("AccY", fontsize='large')
axes[1, 0].yaxis.set_label_coords(-0.07,0.5)
sns.lineplot(ax=axes[2, 0], x=xtypical, y=typicalDF.AccZ, color='b')
axes[2, 0].set_ylabel("AccZ", fontsize='large')
axes[2, 0].yaxis.set_label_coords(-0.07,0.5)
axes[2, 0].set_xlabel("Time / s", fontsize='large')

# Unhealthy
sns.lineplot(ax=axes[0, 1], x=xnontypical, y=nonTypicalDF.AccX, color='g')
axes[0, 1].set_title("Participant with Parkinson's", fontsize='x-large')
axes[0, 1].yaxis.set_visible(False)
sns.lineplot(ax=axes[1, 1], x=xnontypical, y=nonTypicalDF.AccY, color='r')
axes[1, 1].yaxis.set_visible(False)
sns.lineplot(ax=axes[2, 1], x=xnontypical, y=nonTypicalDF.AccZ, color='b')
axes[2, 1].yaxis.set_visible(False)
axes[2, 1].set_xlabel("Time / s", fontsize='large')

plt.tight_layout()
plt.show()