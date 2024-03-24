import os

import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt


def read_ear_marker(filepath):
    """ Extract Wrist and Shank data from c3d and save in """
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    end_fr = itf.GetVideoFrame(1)
    n_frs = end_fr - start_fr + 1

    mkr_data = np.zeros((n_frs, 3), dtype=np.float32)
    mkr_num = 17
    for j in range(3):
        mkr_data[:, j] = np.asarray(itf.GetPointDataEx(16, j, start_fr, end_fr, '1'), dtype=np.float32)

    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return mkr_data

def main():
    subjectPath = "C:/Users/teri-/Downloads/A096391_58_0002.c3d"
    saveName = "A096391_58_0002.csv"
    savePath = "/"
    print(subjectPath)
    mkr_data = read_ear_marker(subjectPath)
    print(mkr_data)
    print("Saving to: ")
    print(saveName)
    np.savetxt(saveName, mkr_data, delimiter=",")

    plt.plot(mkr_data[:, 0] / max(mkr_data[:, 0]))
    plt.show()


if __name__ == "__main__":
    main()
