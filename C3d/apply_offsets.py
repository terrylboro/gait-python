import os
import pandas as pd
import json
from find_gait_event_optical import find_trial_nums

subject = 22
subjectPath = "CombinedData/" #TF_" + str(subject).zfill(2) + ".json"
offsetDF = pd.read_csv("offsets.csv")


def load_json(filepath, offsetDF, subjectNum):
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
        print(data)
        shoeBoxTrialFiles = os.listdir(
            "../TiltCorrectedData/TF_{}/ShoeBox/Right/".format(str(subjectNum).zfill(2)))
        shoeBoxTrialNums = find_trial_nums(shoeBoxTrialFiles)
        for trial in data.keys():
            if int(trial) in shoeBoxTrialNums:
                # load the json data
                # json_str = json.dumps(data[str(trial).zfill(4)])
                # print(json_str)
                # load the offset
                offset = int(offsetDF.loc[offsetDF.Trial==int(trial), "Offset"])
                # print(data[trial])
                # iterate through the string and add offset to each value
                for event in data[trial].keys():
                    data[trial][event] = [x + offset for x in data[trial][event]]
        return data


for subject in os.listdir(subjectPath):
    goodSubjects = open("../Utils/goodTrials",
                        "r").read()
    print(subject)
    subjectNum = int(subject.split("_")[1][0:2])
    if ","+str(subjectNum).zfill(2)+"," in goodSubjects:
        # load up correct df
        subjectOffsetDF = offsetDF[offsetDF['Subject'] == subjectNum]
        subjectOffsetDF = subjectOffsetDF[["Trial", "Offset"]]
        filepath = subjectPath + subject
        offsetDict = load_json(filepath, subjectOffsetDF, subjectNum)
        out_file = open(subject, "w")
        json.dump(offsetDict, out_file, indent=4)


