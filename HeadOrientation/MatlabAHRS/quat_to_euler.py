# Implementation of Kuiper's method to convert quaternion to Euler angles
# This is the method underlying eulerd.m (qparts2feul.m) in Matlab
# https://ocw.mit.edu/courses/16-333-aircraft-stability-and-control-fall-2004/9f042ee5f0597fd8913f6ac53bbb917b_lecture_3.pdf
# Only implemented zyx here

import numpy as np

# case 'ZYX'
#         tmp = qb.*qd.*the2 - qa.*qc.*the2;
#         tmp(tmp > the1) = the1;
#         tmp(tmp < -the1) = -the1;
#         tolA = cast(0.5.*pi - 10.*eps(the1), 'like', tmp);
#         tolB = cast(-0.5.*pi + 10.*eps(the1), 'like', tmp);
#         for ii=1:numel(tmp)
#             b(ii) = -asin(tmp(ii));
#             if b(ii) >=  tolA
#                 a(ii) = -2.*atan2(qb(ii),qa(ii));
#                 c(ii) = 0;
#             elseif b(ii) <= tolB
#                 a(ii) = 2.*atan2(qb(ii),qa(ii));
#                 c(ii) = 0;
#             else
#                 a(ii) = atan2((qa(ii).*qd(ii).*the2 + qb(ii).*qc(ii).*the2),(qa(ii).^2.*the2 - the1 + qb(ii).^2.*the2));
#                 c(ii) = atan2((qa(ii).*qb(ii).*the2 + qc(ii).*qd(ii).*the2),(qa(ii).^2.*the2 - the1 + qd(ii).^2.*the2));
#             end
#         end


def quat_array_to_euler(q):
    # rearrange the format of the quaternions to fit the formula
    qa = q[:, 3]
    qb = q[:, 0]
    qc = q[:, 1]
    qd = q[:, 2]
    # initialise some empty column arrays for euler ZYX which we can fill
    a = np.zeros((len(qa), 1))
    b = np.zeros((len(qb), 1))
    c = np.zeros((len(qc), 1))
    tmp = qb * qd * 2 - qa * qc * 2
    # print(tmp)
    # print(len(tmp))
    for i in range(0, len(tmp)):
        b[i] = -np.arcsin(tmp[i])
        if b[i] >= 0.5 * np.pi:
            a[i] = -2 * np.arctan2(qb[i], qa[i])
            c[i] = 0
        elif b[i] <= -0.5 * np.pi:
            a[i] = 2 * np.arctan2(qb[i], qa[i])
            c[i] = 0
        else:
            a[i] = np.arctan2((qa[i] * qd[i] * 2 + qb[i] * qc[i] * 2), (qa[i] ** 2 * 2 - 1 + qb[i] ** 2 * 2))
            c[i] = np.arctan2((qa[i] * qb[i] * 2 + qc[i] * qd[i] * 2), (qa[i] ** 2 * 2 - 1 + qd[i] ** 2 * 2))
    # print(a)
    euler_angles = np.concatenate((a, b, c), axis=1)
    euler_angles = 180 / np.pi * euler_angles
    return euler_angles


def main():
    q = np.loadtxt("C:/Users/teri-/PycharmProjects/headinspace/Visualisation/"
                   "20231005-Vicon/forward flexion (pitch)_NED_left-quaternion.csv",
                   delimiter=',')
    # print(q)
    euler_angles = quat_array_to_euler(q)
    print(euler_angles)

if __name__ == "__main__":
    main()
