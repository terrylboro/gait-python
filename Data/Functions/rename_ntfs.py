import os

for root, dirs, files in os.walk("../"):
    if "NTF" in root:
        print(root)
        # newDir = root.replace("NTF", "TF")
        # os.mkdir(newDir)
        for name in files:
            print(name)
            old_name = os.path.join(root, name)
            new_name = old_name.replace("NTF", "TF")
            print(new_name)
            os.rename(old_name, new_name)
