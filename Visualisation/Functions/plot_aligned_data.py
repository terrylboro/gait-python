import os
import pandas as pd
import matplotlib.pyplot as plt

for subjectNum in [49]:
    subjectDir = "../../AlignedData/TF_{}".format(str(subjectNum).zfill(2))
    for file in os.listdir(subjectDir)[0:]:
        data = pd.read_csv(os.path.join(subjectDir, file))
        # plt.plot(-data[["AccXShank", "AccYShank", "AccZShank"]])
        plt.plot(data[["AccYchest"]])
        plt.plot(-data[["AccYpocket"]])
        plt.legend(["Ear", "Chest", "Shank"])
        plt.title(file)
        plt.show()
