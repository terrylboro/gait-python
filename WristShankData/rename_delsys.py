import os


def rename_delsys(subjectStart, subjectEnd, activityTypes=["Walk"]):
    # all the subfolders in the "/WristShankData/" folder in a list
    for subject_num in range(subjectStart, subjectEnd):
        subject = "TF_" + str(subject_num).zfill(2)
        for side in ["Shank", "Wrist"]:
            for activity in activityTypes:
                loaddir = subject + "/" + activity + "/" + side + "/"
                if os.path.isdir(loaddir):
                    for file in os.listdir(loaddir):
                        renamed = file.replace("A096391_01_00", subject + "-")
                        os.rename(loaddir + file, loaddir + renamed)


def main():
    rename_delsys(1, 15)


if __name__ == "__main__":
    main()

