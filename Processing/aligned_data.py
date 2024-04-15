import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

subjectDir = "../AlignedData/TF_58/"

data = pd.read_csv(subjectDir + "58-07.txt")
print(data)

# data.plot()
# plt.show()