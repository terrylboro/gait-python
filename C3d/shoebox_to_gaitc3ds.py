import os

c3dDir = "C:/Users/teri-/Documents/GaitC3Ds/"
shoeboxDir = "C:/Users/teri-/Downloads/ShoeBox/"
# c3dDir = "../WristShankData/"

for subjectNum in [x for x in range(34, 68) if x not in [40, 41, 46, 47, 48, 61]]:
    for file in os.listdir(shoeboxDir):
        if "_"+str(subjectNum)+"_" in file:
            oldLoc = shoeboxDir+file
            newLoc = c3dDir+"TF_{}/".format(str(subjectNum).zfill(2))+file
            print(oldLoc,newLoc)
            os.replace(oldLoc, newLoc)


# for path, subdirs, files in os.walk(c3dDir):
#     for name in files:
#         if "gait" not in name:
#             if "A096391" in name and "_67_" in name:
#                 print(name)
#                 # os.remove(os.path.join(path, name))
#                 old_name = os.path.join(path, name)
#                 new_name = old_name.replace("A096391", "TF")
#                 os.rename(old_name, new_name)