import os
import pandas as pd

overallDF = pd.DataFrame(columns=["Subject", "Trial", "Left Stride Time Shank", "Left Stride Time GT", "Left Stride Time Diff",
                                    "Left Stance Time Shank", "Left Stance Time GT", "Left Stance Time Diff",
                                    "Left Swing Time Shank", "Left Swing Time GT", "Left Swing Time Diff"])

# tspDir = "../Shank/Events/Gyro/Comparison/"
# tspDir = "../Ear/Events/AdaptedDiao/Comparison/"
tspDir = "../Chest/Events/McCamley/Comparison/"
for file in os.listdir(tspDir):
    if file.endswith(".csv"):
        subjectNum = file.split(".")[0]
        print("TF_{}".format(subjectNum.zfill(2)))
        data = pd.read_csv(tspDir+file)
        data.insert(0, "Subject", subjectNum)
        data["Subject"] = subjectNum
        overallDF = overallDF.append(data, ignore_index=True)

# overallDF.to_csv(tspDir+"ShankGyroComparison.csv", index=False)
# overallDF.to_csv(tspDir+"EarAdaptedDiaoComparison.csv", index=False)
overallDF.to_csv(tspDir+"ChestMcCamleyComparison.csv", index=False)
