import os
import pandas as pd

for file in os.listdir(os.getcwd()):
    if file.endswith(".csv"):
        df = pd.read_csv(file)
        if (df < 0).any(axis=1).any():
            print(file)
            print(df[(df < 0).any(axis=1)].Trial)
