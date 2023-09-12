# A script to implement the singular spectrum analysis method described by Jarchi et al.
# https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6710137
# Handy Python tutorial here: https://www.kaggle.com/code/jdarcy/introducing-ssa-for-time-series-decomposition
# Class is simply lifted from this tutorial

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class SSA(object):
    __supported_types = (pd.Series, np.ndarray, list)

    def __init__(self, tseries, L, save_mem=True):
        """
        Decomposes the given time series with a singular-spectrum analysis. Assumes the values of the time series are
        recorded at equal intervals.

        Parameters
        ----------
        tseries : The original time series, in the form of a Pandas Series, NumPy array or list.
        L : The window length. Must be an integer 2 <= L <= N/2, where N is the length of the time series.
        save_mem : Conserve memory by not retaining the elementary matrices. Recommended for long time series with
            thousands of values. Defaults to True.

        Note: Even if an NumPy array or list is used for the initial time series, all time series returned will be
        in the form of a Pandas Series or DataFrame object.
        """

        # Tedious type-checking for the initial time series
        if not isinstance(tseries, self.__supported_types):
            raise TypeError("Unsupported time series object. Try Pandas Series, NumPy array or list.")

        # Checks to save us from ourselves
        self.N = len(tseries)
        if not 2 <= L <= self.N / 2:
            raise ValueError("The window length must be in the interval [2, N/2].")

        self.L = L
        self.orig_TS = pd.Series(tseries)
        self.K = self.N - self.L + 1

        # Embed the time series in a trajectory matrix
        self.X = np.array([self.orig_TS.values[i:L + i] for i in range(0, self.K)]).T

        # Decompose the trajectory matrix
        self.U, self.Sigma, VT = np.linalg.svd(self.X)
        self.d = np.linalg.matrix_rank(self.X)

        self.TS_comps = np.zeros((self.N, self.d))

        if not save_mem:
            # Construct and save all the elementary matrices
            self.X_elem = np.array([self.Sigma[i] * np.outer(self.U[:, i], VT[i, :]) for i in range(self.d)])

            # Diagonally average the elementary matrices, store them as columns in array.
            for i in range(self.d):
                X_rev = self.X_elem[i, ::-1]
                self.TS_comps[:, i] = [X_rev.diagonal(j).mean() for j in range(-X_rev.shape[0] + 1, X_rev.shape[1])]

            self.V = VT.T
        else:
            # Reconstruct the elementary matrices without storing them
            for i in range(self.d):
                X_elem = self.Sigma[i] * np.outer(self.U[:, i], VT[i, :])
                X_rev = X_elem[::-1]
                self.TS_comps[:, i] = [X_rev.diagonal(j).mean() for j in range(-X_rev.shape[0] + 1, X_rev.shape[1])]

            self.X_elem = "Re-run with save_mem=False to retain the elementary matrices."

            # The V array may also be very large under these circumstances, so we won't keep it.
            self.V = "Re-run with save_mem=False to retain the V matrix."

        # Calculate the w-correlation matrix.
        self.calc_wcorr()

    def components_to_df(self, n=0):
        """
        Returns all the time series components in a single Pandas DataFrame object.
        """
        if n > 0:
            n = min(n, self.d)
        else:
            n = self.d

        # Create list of columns - call them F0, F1, F2, ...
        cols = ["F{}".format(i) for i in range(n)]
        return pd.DataFrame(self.TS_comps[:, :n], columns=cols, index=self.orig_TS.index)

    def reconstruct(self, indices):
        """
        Reconstructs the time series from its elementary components, using the given indices. Returns a Pandas Series
        object with the reconstructed time series.

        Parameters
        ----------
        indices: An integer, list of integers or slice(n,m) object, representing the elementary components to sum.
        """
        if isinstance(indices, int): indices = [indices]

        ts_vals = self.TS_comps[:, indices].sum(axis=1)
        return pd.Series(ts_vals, index=self.orig_TS.index)

    def trend_removal(self):
        """
        Same as reconstruct but includes all components aside from #1 (the trend) then add the mean
        :return: trend-removed time series
        """
        ts_vals = self.TS_comps[:, 1:len(self.TS_comps)].sum(axis=1)
        tred_removed_vals = ts_vals + self.orig_TS.mean()
        return pd.Series(tred_removed_vals, index=self.orig_TS.index)

    def calc_wcorr(self):
        """
        Calculates the w-correlation matrix for the time series.
        """

        # Calculate the weights
        w = np.array(list(np.arange(self.L) + 1) + [self.L] * (self.K - self.L - 1) + list(np.arange(self.L) + 1)[::-1])

        def w_inner(F_i, F_j):
            return w.dot(F_i * F_j)

        # Calculated weighted norms, ||F_i||_w, then invert.
        F_wnorms = np.array([w_inner(self.TS_comps[:, i], self.TS_comps[:, i]) for i in range(self.d)])
        F_wnorms = F_wnorms ** -0.5

        # Calculate Wcorr.
        self.Wcorr = np.identity(self.d)
        for i in range(self.d):
            for j in range(i + 1, self.d):
                self.Wcorr[i, j] = abs(w_inner(self.TS_comps[:, i], self.TS_comps[:, j]) * F_wnorms[i] * F_wnorms[j])
                self.Wcorr[j, i] = self.Wcorr[i, j]

    def plot_wcorr(self, min=None, max=None):
        """
        Plots the w-correlation matrix for the decomposed time series.
        """
        if min is None:
            min = 0
        if max is None:
            max = self.d

        if self.Wcorr is None:
            self.calc_wcorr()

        ax = plt.imshow(self.Wcorr)
        plt.xlabel(r"$\tilde{F}_i$")
        plt.ylabel(r"$\tilde{F}_j$")
        plt.colorbar(ax.colorbar, fraction=0.045)
        ax.colorbar.set_label("$W_{i,j}$")
        plt.clim(0, 1)

        # For plotting purposes:
        if max == self.d:
            max_rnge = self.d - 1
        else:
            max_rnge = max

        plt.xlim(min - 0.5, max_rnge + 0.5)
        plt.ylim(max_rnge + 0.5, min - 0.5)






# def ssa(data):
#     L = 70  # window length / embedding dimension
#     N = len(data)
#
#     # Normalise the data and remove mean
#     data = (data - np.mean(data)) / np.std(data)
#
#     # Calculate the covariance matrix, X (trajectory)
#     # time series s of length n is converted to an L x N matrix (trajectory matrix), X
#     K = N - L + 1  # The number of columns in the trajectory matrix.
#     X = np.column_stack([data[i:i+L] for i in range(0, K)])
#     # Note: the i+L above gives us up to i+L-1, as numpy array upper bounds are exclusive.
#     display_traj_mat(X)
#
#     # Decomposition of trajectory matrix
#     d = np.linalg.matrix_rank(X)  # The intrinsic dimensionality of the trajectory space.
#     U, Sigma, V = np.linalg.svd(X)
#     V = V.T  # Note: the SVD routine returns V^T, not V
#     X_elem = np.array([Sigma[i] * np.outer(U[:, i], V[:, i]) for i in range(0, d)])
#     # Quick sanity check: the sum of all elementary matrices in X_elm should be equal to X, to within a
#     # *very small* tolerance:
#     if not np.allclose(X, X_elem.sum(axis=0), atol=1e-10):
#         print("WARNING: The sum of X's elementary matrices is not equal to X!")
#
#     n = min(12, d)  # In case d is less than 12 for the toy series. Say, if we were to exclude the noise component...
#     for i in range(n):
#         plt.subplot(4, 4, i + 1)
#         title = "$\mathbf{X}_{" + str(i) + "}$"
#         plot_2d(X_elem[i], title)
#     plt.tight_layout()
#
#     sigma_sumsq = (Sigma ** 2).sum()
#     fig, ax = plt.subplots(1, 2, figsize=(14, 5))
#     ax[0].plot(Sigma ** 2 / sigma_sumsq * 100, lw=2.5)
#     ax[0].set_xlim(0, 11)
#     ax[0].set_title("Relative Contribution of $\mathbf{X}_i$ to Trajectory Matrix")
#     ax[0].set_xlabel("$i$")
#     ax[0].set_ylabel("Contribution (%)")
#     ax[1].plot((Sigma ** 2).cumsum() / sigma_sumsq * 100, lw=2.5)
#     ax[1].set_xlim(0, 11)
#     ax[1].set_title("Cumulative Contribution of $\mathbf{X}_i$ to Trajectory Matrix")
#     ax[1].set_xlabel("$i$")
#     ax[1].set_ylabel("Contribution (%)");
#
#     plt.show()
#
#
#
#
#
# def display_traj_mat(X):
#     ax = plt.matshow(X)
#     plt.xlabel("$L$-Lagged Vectors")
#     plt.ylabel("$K$-Lagged Vectors")
#     plt.colorbar(ax.colorbar, fraction=0.025)
#     ax.colorbar.set_label("$F(t)$")
#     plt.title("The Trajectory Matrix for the Toy Time Series")
#     # plt.show()
#
# # A simple little 2D matrix plotter, excluding x and y labels.
# def plot_2d(m, title=""):
#     plt.imshow(m)
#     plt.xticks([])
#     plt.yticks([])
#     plt.title(title)


def main():
    data = np.loadtxt("/Data/Amy/amy-15.txt", delimiter=',', usecols=[2, 3, 4])
    window = 70
    title_order = ['AP Axis', 'SI Axis', 'ML Axis']
    # demo_ssa = SSA(data, window)
    # demo_ssa.plot_wcorr()
    # plt.title("W-Correlation for Walking Time Series")

    for i in range(0, 3):
        # begin reconstructing the components etc.
        plt.figure(i)
        # perform SSA on given axis
        axis_data = SSA(data[:, i], window)
        # demo_ssa.reconstruct(0).plot()
        axis_data.reconstruct([1, 2]).plot()

        axis_data.orig_TS.plot(alpha=0.4)
        plt.title(title_order[i])
        plt.xlabel(r"$t$ (s)")
        plt.ylabel("Acceleration (G)")
        legend = [r"$\tilde{{F}}^{{({0})}}$".format(i) for i in range(1)] + ["Original TS"]
        plt.legend(legend)

    plt.show()



if __name__ == '__main__':
    main()






