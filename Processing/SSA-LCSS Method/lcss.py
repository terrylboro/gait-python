# Implementation of Vlachos et al. lcsMatching code

import numpy as np
import matplotlib.pyplot as plt


def lcsMatching(a, b, delta, epsilon):
    """
    INPUT:
    :param a: [m x 1] time series A\n
    :param b: [n x 1] time series B\n
    :param delta: time matching region (left & right)\n
    :param epsilon: spatial matching region (up & down)\n
    :return: The similarity between A and B defined as LCSS(A,B) / max(|A|, |B|)
    """
    m = len(a)
    n = len(b)
    # Ensure shortest is first
    if n < m:
        temp = a
        a = b
        b = temp
        m = len(a)
        n = len(b)
    lcstable = np.zeros((m+1, n+1))
    prevx = np.zeros((m + 1, n + 1))
    prevy = np.zeros((m + 1, n + 1))
    for i in range(0, m):
        for j in range(i - delta, i + delta):
            if 0 < j < n:
                if b[j] + epsilon >= a[i] >= b[j] - epsilon:
                    lcstable[i+1, j+1] = lcstable[i, j] + 1
                    prevx[i+1, j+1] = i
                    prevy[i+1, j+1] = j
                elif lcstable[i, j+1] > lcstable[i+1, j]:
                    lcstable[i + 1, j + 1] = lcstable[i, j+1]
                    prevx[i + 1, j + 1] = i
                    prevy[i + 1, j + 1] = j + 1
                else:
                    lcstable[i + 1, j + 1] = lcstable[i + 1, j]
                    prevx[i + 1, j + 1] = i + 1
                    prevy[i + 1, j + 1] = j
    # Get rid of initial conditions
    lcstable = lcstable[1:, 1:]
    prevx = prevx[1:, 1:] - 1
    prevy = prevy[1:, 1:] - 1
    # LCS similarity
    lcs = max(lcstable[m-1, :])
    pos = np.argmax(lcstable[m-1, :])
    similarity = lcs / (max(m-1, n))
    # Optimal path of dynamical programming
    now = np.array([m-1, pos])
    prev = np.array([prevx[now[0], now[1]], prevy[now[0], now[1]]]).astype(np.int32)
    print(prev)
    lcs_path = now
    while np.min(prev) >= 0:
        now = prev
        prev = np.array([prevx[now[0], now[1]], prevy[now[0], now[1]]]).astype(np.int32)
        lcs_path = np.vstack([lcs_path, now])
    lcs_path = np.flipud(lcs_path)
    # Matching points
    print(lcs_path)
    print(lcstable)
    print([lcs_path[:, 1] ] * (m-2))
    print(lcs_path[:, 0])
    temp = lcstable[[lcs_path[:, 1]] * (m-2) + lcs_path[:, 0] - 1]  # LCS count along the path
    temp = np.vstack([0, temp])
    index = np.diff(temp)
    match_point = lcs_path[index, :]

    # Plot matching region and point correspondence
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    create_envelope(b, delta, epsilon, ax1)
    ax1.plot(a, 'r-')
    ax1.plot(b, 'b-')
    # --------------
    a = (a - np.mean(a)) / np.std(a)
    b = (b - np.mean(b)) / np.std(b)
    transpose = 5

    for i in range(0, len(match_point)):
        s = match_point[i, 0]
        e = match_point[i, 1]
        h = plt.quiver((s, e), (a(s), b(e) - transpose))

    ax2.plot(a, 'r-')
    ax2.plot(b-transpose, 'b-')

    return similarity, match_point



def create_envelope(traj, window, epsilon, ax):
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html#sphx-glr-gallery-lines-bars-and-markers-fill-between-demo-py
    [tt, n] = np.shape(traj)
    U = np.zeros((1,n))
    L = np.zeros((1, n))

    U[0] = max(traj[0, 0:window] + epsilon)
    L[0] = min(traj[0, 0:window] - epsilon)

    for i in range(0, n):
        pLow = i - window
        pHigh = i + window
        if i < window + 1:
            pLow = 1
        if i + window > n:
            pHigh = n

        U[i] = max(traj[0, pLow:pHigh] + epsilon)
        L[i] = min(traj[0, pLow:pHigh] - epsilon)

    # Plot area
    x = range(0, n)
    plt.fill_between(x, L, U, alpha=0.2)


def main():
    print("IMPLEMENT THIS")



if __name__ == '__main__':
    main()
