import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt


def get_heel_trajectory(filepath):
    """ 14 = RHEE 9 = LHEE """
    # Get the COM object of C3Dserver
    itf = c3d.c3dserver()
    # Open a C3D file
    ret = c3d.open_c3d(itf, filepath)
    # Determine start and end frame numbers (to compensate for cropping)
    start_fr = itf.GetVideoFrame(0)
    end_fr = itf.GetVideoFrame(1)
    n_frs = end_fr - start_fr + 1

    mkr_RHEE = c3d.get_marker_index(itf, "RHEE")
    mkr_LHEE = c3d.get_marker_index(itf, "LHEE")

    fp_1 = np.zeros(((end_fr+1) * 20), dtype=np.float32)
    fp_2 = np.zeros(((end_fr+1) * 20), dtype=np.float32)

    fp_1[start_fr * 20:] = np.asarray(itf.GetAnalogDataEx(2, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    fp_2[start_fr * 20:] = np.asarray(itf.GetAnalogDataEx(8, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    heel_data_l = np.zeros((end_fr+1, 3), dtype=np.float32)
    heel_data_r = np.zeros((end_fr+1, 3), dtype=np.float32)
    for j in range(3):
        heel_data_l[start_fr:, j] = np.asarray(itf.GetPointDataEx(mkr_LHEE, j, start_fr, end_fr, '1'), dtype=np.float32)
        heel_data_r[start_fr:, j] = np.asarray(itf.GetPointDataEx(mkr_RHEE, j, start_fr, end_fr, '1'), dtype=np.float32)


    # Close the C3D file from C3Dserver
    ret = c3d.close_c3d(itf)
    return heel_data_l, heel_data_r, fp_1, fp_2


def IC_from_fp(fp_data):
    return int(round(np.where(fp_data < -10)[0][0] / 20)-1)

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size // 2:]

# def find_other_ICs(heel_data_l, fp_IC):



def main():
    filepath = "C:/Users/teri-/Downloads/A096391_58_0009.c3d"
    heel_data_l, heel_data_r, fp_1, fp_2 = get_heel_trajectory(filepath)
    l_IC = IC_from_fp(fp_1)
    r_IC = IC_from_fp(fp_2)
    # autocorrelation
    # z = autocorr(heel_data_l[:, 2])
    # z2 = autocorr(heel_data_r[:, 2])
    # plt.plot(z / float(z.max()), "r--", label="Left")
    # plt.plot(z2 / float(z.max()), "g--", label="Right")
    # plt.legend()
    # plt.title("Autocorrelation")
    plt.plot(heel_data_l[:, 2] / float(heel_data_l.max()), label="Left")
    plt.plot(heel_data_r[:, 2] / float(heel_data_r.max()), label="Right")
    # plt.plot(fp_1[0::20])
    # plt.plot(fp_2[0::20])
    plt.vlines([r_IC, l_IC], 0, 1)
    plt.show()


if __name__ == "__main__":
    main()