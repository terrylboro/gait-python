import os

for subjectnum in range(0, 65):
    os.mkdir("TF_{}".format(str(subjectnum).zfill(2)))
