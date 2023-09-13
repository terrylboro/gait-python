import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_gait_data(data, title, save_dir=None, plot_legend=True, chest=False):
    """
    Plot the accelerometer data from a gait experiment trial
    :param data: The three accelerometer columns
    :param title: The title for the plot
    :param save_dir: Directory to save plot if desired
    :param save: Figure is saved if set true (default)
    :return: A plot of the three accelerometer axes
    """
    # Firstly, perform some data parsing
    left_cols = ['AccXlear', 'AccYlear', 'AccZlear']
    right_cols = ['AccXrear', 'AccYrear', 'AccZrear']
    chest_cols = ['AccXchest', 'AccYchest', 'AccZchest']
    cols = [left_cols, right_cols] if not chest else [left_cols, right_cols, chest_cols]
    fig_num = 1
    plt.close('all')

    for col in cols:
        plt.figure(fig_num)
        fig_num += 1
        plt.plot(data[col[0]].values, 'c-')
        plt.plot(data[col[1]].values, 'm-')
        plt.plot(data[col[2]].values, 'y-')
        plt.ylabel(r'Acceleration / $ms^{-2}$')
        plt.xlabel('Samples')
        if col == left_cols:
            plt.title(title+" left")
        elif col == right_cols:
            plt.title(title+" right")
        else:
            plt.title(title + " chest")
        # Setup legend below the plots
        ax = plt.gca()
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.85])
        if plot_legend:
            # Put a legend below current axis
            ax.legend(['Anterior/Posterior', 'Superior/Inferior', 'MedioLateral'], loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fancybox=True, shadow=True, ncol=5)

        if save_dir is not None:
            plt.savefig(save_dir+title+".png", format="png")


    # plt.close()

def main():
    # colNames = ['Frame', 'Time']
    # imu_locations = ['lear', 'rear', 'chest', 'pocket']
    # repeated_headers = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ']
    # for i in range(0, 4):
    #     elements = [element+imu_locations[i] for element in repeated_headers]
    #     # print(elements)
    #     colNames.extend(elements)
    # print(colNames)

    colNames = np.loadtxt("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/columnHeaders", delimiter=',', dtype=str)

    data = pd.read_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Data/Amy/Static/amy-static.txt", names=colNames)
    print(data)
    # plot_gait_data(data, "example")


if __name__ == "__main__":
    main()
