import os

c3dDir = "C:/Users/teri-/Documents/GaitC3Ds/"
shoeboxDir = "C:/Users/teri-/Downloads/ShoeBox/"

# for path, subdirs, files in os.walk(c3dDir):
#     for name in files:
#         if "A096391" in name:
#             old_name = os.path.join(path, name)
#             new_name = old_name.replace("A096391", "TF")
#             if not os.path.exists(new_name):
#                 os.rename(old_name, new_name)
#             else:
#                 os.remove(old_name)
#             if "15_CU_" in new_name:
#                 old_name = os.path.join(path, new_name)
#                 new_name = old_name.replace("15_CU_", "")
#                 if not os.path.exists(new_name):
#                     os.rename(old_name, new_name)
#                 else:
#                     os.remove(old_name)

for subjectNum in [x for x in range(60, 68) if x not in [40, 41, 46, 47, 48, 61]]:
    for file in os.listdir(shoeboxDir):
        if "_"+str(subjectNum) in file:
            if "A096391" in file:
                old_name = os.path.join(shoeboxDir, file)
                new_name = old_name.replace("A096391", "TF")
                if not os.path.exists(new_name):
                    os.rename(old_name, new_name)
                else:
                    os.remove(old_name)
                if "15_CU_" in new_name:
                    old_name = os.path.join(shoeboxDir, new_name)
                    new_name = old_name.replace("15_CU_", "")
                    if not os.path.exists(new_name):
                        os.rename(old_name, new_name)
                    else:
                        os.remove(old_name)
            oldLoc = new_name.split("/")[-1]
            newLoc = c3dDir+"TF_{}/".format(str(subjectNum).zfill(2))+oldLoc
            print(oldLoc,newLoc)
            os.replace(shoeboxDir+oldLoc,newLoc)



