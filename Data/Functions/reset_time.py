# set the timestamps of a given trial to start from time of first, non-cropped sample

import numpy as np
import pandas as pd
import os


def reset_time(df):
    print("To implemtn")

def main():
    subject = "TomBrace"
    cropped_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/CroppedWalk/"
    og_data_filepath = "C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/" + subject + "/Walk/"
    cropped_filenames = ["tombrace-2.txt", "tombrace-3.txt", "tombrace-4.txt", "tombrace-5.txt"]
    og_filenames = ["kneebrace-straight-1.txt", "kneebrace-straight-2.txt", "kneebrace-bent-1.txt", "kneebrace-bent-2.txt"]
    count = 0
    for file in os.listdir(cropped_filepath):
        if file.endswith(".txt"):
            cropped_df = pd.read_csv(cropped_filepath+cropped_filenames[count], delimiter=',')
            og_df = pd.read_csv(og_data_filepath+og_filenames[count], delimiter=',', header=None)
            cropped_df['Time'] = (cropped_df['Time'] - og_df.at[0, 1]) / 10**6
            print(cropped_df)
            cropped_df.drop('Frame', axis=1, inplace=True)
            cropped_df.to_csv(cropped_filepath+cropped_filenames[count], index=None)
            count += 1


if __name__ == "__main__":
    main()
