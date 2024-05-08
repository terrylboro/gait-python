import os
import pandas as pd

overallDF = pd.DataFrame(columns=["Subject", "Trial", "Left Stride Time Shank", "Left Stride Time GT", "Left Stride Time Diff",
                                    "Left Stance Time Shank", "Left Stance Time GT", "Left Stance Time Diff",
                                    "Left Swing Time Shank", "Left Swing Time GT", "Left Swing Time Diff"])

for file in os.listdir(os.getcwd()):
    if file.endswith(".csv"):
        subjectNum = file.split(".")[0]
        data = pd.read_csv(file)
        data.insert(0, "Subject", subjectNum)
        data["Subject"] = subjectNum
        overallDF = overallDF.append(data, ignore_index=True)

overallDF.to_csv("EarablesAdaptedDiaoComparison.csv", index=False)
