import os

# Open a txt file to write info to
txtfile = open("info.txt", "w")

for subjectNum in range(34, 67):
    subjectDir = "../TF_{}".format(str(subjectNum).zfill(2))
    txtfile.write(str(subjectNum) + ":")
    if "Walk" in os.listdir(subjectDir):
        txtfile.write("\nStandard Walk:")
        walkTrials = os.listdir(os.path.join(subjectDir, "Walk"))
        for trial in walkTrials:
            txtfile.write(trial + " ")
    if "Floor2Turf" in os.listdir(subjectDir):
        print(os.listdir(os.path.join(subjectDir, "Floor2Turf")))
        f2tTrials = os.listdir(os.path.join(subjectDir, "Floor2Turf"))
        txtfile.write("\nFloor2Turf: ")
        for trial in f2tTrials:
            txtfile.write(trial + " ")
    if "Turf2Floor" in os.listdir(subjectDir):
        print(os.listdir(os.path.join(subjectDir, "Turf2Floor")))
        t2fTrials = os.listdir(os.path.join(subjectDir, "Turf2Floor"))
        txtfile.write("\nTurf2Floor: ")
        for trial in t2fTrials:
            txtfile.write(trial + " ")
    txtfile.write("\n")

txtfile.close()


