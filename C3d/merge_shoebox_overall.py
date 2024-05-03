import json
import os
from find_gait_event_optical import find_trial_nums

overallDir = "OwnGroundTruth/RawEventsWalksAndTurf/"
shoeboxDir = os.getcwd()
dataDir = "../TiltCorrectedData/"


def load_shoebox_json(filepath):
    # read json file
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
        print(data.keys())
        return json.dumps(data)


def insert_shoebox(shoeboxfp, overallfp):
    with open(shoeboxfp, 'r') as shoeboxfile:
        sbData = json.load(shoeboxfile)
    with open(overallfp, 'r') as overallfile:
        oData = json.load(overallfile)
    # print(oData[sbData.keys()[1]])
    for key in sbData.keys():
        if key not in oData.keys():
            oData[key] = sbData[key]
    return oData


for subjectNum in [x for x in range(34, 68) if x not in [40, 41, 46, 47, 48, 61]]:
    # Find the ShoeBox trials for this subject
    shoeBoxTrialFiles = os.listdir(
        "../TiltCorrectedData/TF_{}/ShoeBox/Right/".format(str(subjectNum).zfill(2)))
    shoeBoxTrialNums = find_trial_nums(shoeBoxTrialFiles)
    # loop through these subject/trial combos to find correct Jsons
    combinedJsonStr = insert_shoebox(shoeboxDir + "/TF_{}.json".format(subjectNum),
                                     overallDir + "/TF_{}.json".format(subjectNum))
    subject = "CombinedData/TF_{}".format(subjectNum)
    out_file = open(subject + ".json", "w")
    json.dump(combinedJsonStr, out_file, indent=4, sort_keys=True)