import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

# load the df
activityName = "WalkShake"
metric = "StanceTime"
data = pd.read_csv('fullCyclesOptical.csv')
data = data[data.Activity == activityName]

# Calculate stride times
data["StrideTime"] = data["IC3"] - data["IC1"]
data["StanceTime"] = data["FO2"] - data["IC1"]
data["SwingTime"] = data["IC3"] - data["FO2"]

# # plot the data for all participants
# ax1 = data[data["Subject"].isin(range(1, 6))].plot.scatter(x="Subject",y=metric,
#                                                              c="TrialNum", colormap="viridis")
# # g = sns.relplot(data=data[data["Subject"].isin(range(1, 68))], x='Subject', y=metric, hue='Condition',
# #             hue_order=["Typical", "Parkinsons", "Comorbities", "Balance"])
# # leg = g._legend
# # leg.set_bbox_to_anchor([0.4, 0.75])  # coordinates of lower left of bounding box
# plt.title("{} {} data for all participants".format(activityName, metric))
# # plt.legend(loc='upper right')
# plt.tight_layout()
# plt.show()

# heatmap plotting
counts = data.groupby(['Subject', metric, "Condition"]).size().reset_index(name='Count')
fig, ax = plt.subplots(figsize=(30, 10))
g = sns.scatterplot(data=counts, x='Subject', y=metric, size='Count', ax=ax, hue="Condition",
                legend="auto")
g.legend(loc = 'center left', bbox_to_anchor = (1, 0.5), ncol = 1)
# leg = g._legend
# leg.set_bbox_to_anchor([0.1, 0.75])  # coordinates of lower left of bounding box
ax.grid(axis='y')
sns.despine(left=True, bottom=True)
plt.title("{} data for all participants during {} task".format(metric, activityName), size='xx-large')
plt.xlabel("Subject", size='xx-large')
plt.ylabel(metric + "* 10/ms", size='xx-large')
plt.tight_layout()
# plt.show()
plt.savefig("Plots/{}{}All.png".format(activityName, metric))
# # heatmap plotting
# subjects = range(1, 68)
# cross = pd.crosstab(data[metric], data["Subject"]).reindex(columns=subjects, fill_value=0)
# fig, ax = plt.subplots(figsize=(30, 10))#figsize=(30, 5)
# sns.heatmap(cross, cbar_kws=dict(label='Count'), ax=ax, cmap="coolwarm")
# ax.invert_yaxis()
# plt.show()

# # Violin Plotting
# fig, axes = plt.subplots(figsize=(60, 20))
# # sns.violinplot(x=data["Subject"], y=data[metric], ax = axes)
# sns.violinplot(data=data[data["Subject"].isin(range(1, 68))],
#                x="Subject", y=metric, hue="Condition")
# axes.set_title('Violin Plot for {}'.format(activityName))
# axes.yaxis.grid(True)
# axes.set_xlabel('Participant')
# axes.set_ylabel(metric)
# plt.show()