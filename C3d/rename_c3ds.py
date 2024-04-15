import os

c3dDir = "C:/Users/teri-/Documents/GaitC3Ds/"
# c3dDir = "../WristShankData/"

# for num in range(0, 10):
#     os.mkdir(c3dDir + "TF_" + str(num).zfill(2) + "/")

for path, subdirs, files in os.walk(c3dDir):
    for name in files:
        if "gait" not in name:
            if "A096391" in name:
                print(name)
                # os.remove(os.path.join(path, name))
                old_name = os.path.join(path, name)
                new_name = old_name.replace("A096391", "TF")
                # if "15_CU_" in new_name:
                #     new_name = old_name.replace("15_CU_", "")
                # trialNum = new_name.split("_")[-1]
                # if trialNum[0:2] != "00":
                #     new_name = ("_".join(new_name.split("_")[0:-1]) + "_" +
                #                 trialNum[0:2].zfill(2) + "_" + trialNum[2:4].zfill(4)) + ".c3d"
                #     print(new_name)
                # if not new_name.endswith(".c3d") and not new_name.endswith(".json"):
                #     new_name = new_name + ".c3d"
                os.rename(old_name, new_name)
