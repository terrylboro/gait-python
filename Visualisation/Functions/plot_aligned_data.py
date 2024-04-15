import os
import pandas as pd
import matplotlib.pyplot as plt

from GroundTruths.Functions.load_ground_truth import load_ground_truth_json_new

for subjectNum in range(62, 64):
    subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
    for file in os.listdir(subjectDir)[3:5]:
        trialNum = int(file.split(".")[0].split("-")[-1])
        data = pd.read_csv(os.path.join(subjectDir, file))
        plt.plot(data["AccZlear"])
        plt.plot(-data["AccZShank"])
        # load the gt data
        df = load_ground_truth_json_new(subjectNum, trialNum)
        print(df)
        plt.vlines(df.iloc[0, :], ymin=0, ymax=10, color='r', linestyle='solid')
        plt.vlines(df.iloc[1, :], ymin=0, ymax=10, color='g', linestyle='solid')
        plt.show()

