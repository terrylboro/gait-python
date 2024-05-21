import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.signal import butter, filtfilt, welch, argrelextrema, windows


def bwfilt(data, btype, freq):
    b, a = butter(2, freq, btype=btype, fs=100, output='ba')
    return filtfilt(b, a, data, axis=0)


def gurchiek(data, minStrideTime, maxStrideTime, minDutyFactor, maxDutyFactor, nMinimumStrides):
    """
    Adapted from Matlab code by Reed Gurchiek, 2020
    identifies instants of stride start (foot contact) and swing start
    (foot off) given accelerometer signal aligned with long axis of thigh
    """
    # initialise
    deleteBout = False
    strideStart, swingStart = [], []
    # get the signal frequency characteristics
    a10 = bwfilt(data, "high", 10)
    plt.plot(data - np.mean(data))
    plt.show()
    freq, fPow = welch(data - np.mean(data), fs=100, window=windows.boxcar(200), nfft=4096)#, window=np.ones(200), nfft=4096)
    fPow = fPow[np.logical_and(freq > 0.5, freq < 4)]
    freq = freq[np.logical_and(freq > 0.5, freq < 4)]
    plt.semilogy(freq, fPow)
    # find extrema of the power spectrum
    iPow = argrelextrema(fPow, np.greater)
    # remove start/end values which are extrema by default
    fPow[iPow == 1] = 0
    fPow[iPow == len(fPow)] = 0
    freq = freq[iPow]
    fPow = fPow[iPow]
    # pick the max values from the power spectrum
    iMax = np.argmax(fPow)
    stpf = freq[iMax]
    print("stpf: ", stpf)
    plt.plot(stpf, fPow[iMax], 'x')
    plt.plot(freq[0], fPow[0], 'x')
    plt.show()
    fPow[freq >= stpf] = 0
    freq[freq >= stpf] = 0
    iMax = np.argmax(fPow)
    strf = freq[iMax]
    print("strf: ", strf)
    # check that both strf and stpf are available, if not delete this bout
    if strf is None or stpf is None:
        deleteBout = True
    else:
        # start the filtering part of the algorithm
        astp = bwfilt(data, 'low', stpf)
        astr = bwfilt(data, 'low', strf)
        astrx = bwfilt(data, 'low', 5 * stpf / 2)
        # get minima/maxima of stride/step filtered signals
        iMaxStr = argrelextrema(astr, np.greater)[0]
        iMinStr = argrelextrema(astr, np.less)[0]
        iMaxStp = argrelextrema(astp, np.greater)[0]
        iMinStp = argrelextrema(astp, np.less)[0]
        iMaxStr[iMaxStr == len(iMaxStr)] = 0
        iMinStr[iMinStr == len(iMinStr)] = 0
        iMaxStp[iMaxStp == len(iMaxStp)] = 0
        iMinStp[iMinStp == len(iMinStp)] = 0
        iMaxStr[iMaxStr == len(iMaxStr)] = 0
        iMinStr[iMinStr == len(iMinStr)] = 0
        iMaxStp[iMaxStp == len(iMaxStp)] = 0
        iMinStp[iMinStp == len(iMinStp)] = 0
        # find 1g crossing points
        iCrossG = np.where(np.diff(np.signbit(astrx - 9.81).flatten()))[0] + 1
        # weird variance correction if there are 2 peaks
        i = 0
        while i <= len(iMinStr) - 2:
            intLength = iMinStr[i+1] - iMinStr[i]
            print("intLength: ", intLength)
            if intLength < np.floor(minStrideTime):
                var1 = np.var(a10[iMinStr[i]:iMinStr[i]+intLength])
                if iMinStr[i+1] + intLength > len(data):
                    var2 = np.var(a10[iMinStr[i+1]:])
                else:
                    var2 = np.var(a10[iMinStr[i+1]:iMinStr[i+1] + intLength])
                # remove one with lesser variance
                if var1 > var2:
                    iMinStr = np.delete(iMinStr, i+1)
                elif var2 > var1:
                    iMinStr = np.delete(iMinStr, i)
                else:
                    # otherwise use one with lowest associated stpf filtered min
                    temp1 = np.argmin(abs(iMinStr[i] - iMinStp))
                    temp2 = np.argmin(abs(iMinStr[i+1] - iMinStp))
                    if temp1 == temp2:
                        if astr[iMinStr[i+1]] < astr[iMinStr]:
                            iMinStr = np.delete(iMinStr, i)
                        else:
                            iMinStr = np.delete(iMinStr, i+1)
                    else:
                        if astp[iMinStp[temp2]] < astp[iMinStp[temp1]]:
                            iMinStr = np.delete(iMinStr, i)
                        else:
                            iMinStr = np.delete(iMinStr, i+1)
            elif iMinStr[i+1] - iMinStr[i] > np.ceil(maxStrideTime):
                iMinStr = np.delete(iMinStr, i)
            else:
                i += 1

        # do some plotting to check
        plt.plot(data)
        plt.plot(astp)
        plt.plot(astr)
        plt.plot(astrx)
        plt.plot(iMinStr, data[iMinStr], '^')
        # need at least 2 more minima than nMinimumStrides
        if len(iMinStr) < nMinimumStrides + 2:
            deleteBout = 1
        else:
            # gait phase detection algorithm
            # last step peak between stride minima = swing start
            # following valley for each stride peak ~ FC
            # next 1g crossing in astrx is best est of FC
            print("\n\n GAIT PHASE DETECTION \n\n")
            print("iMinStr: ", iMinStr)
            swingStart = np.zeros(len(iMinStr))
            strideStart = np.zeros(len(iMinStr))
            i = 0
            while i < len(iMinStr) - 1:
                print(i)
                deleteStride = False
                # get astp peaks between current and next astr minima
                print("iMinStr[i]", iMinStr[i])
                print("iMaxStp", iMaxStp)
                print("iMinStr[i+1]", iMinStr[i+1])
                swingStart0 = iMaxStp[np.logical_and(iMaxStp > iMinStr[i], iMaxStp < iMinStr[i+1])]
                print("swingStart0: ", swingStart0)
                if not len(swingStart0):
                    deleteStride = True
                else:
                    # if 1 peak then this is our estimate
                    # if 2 peaks then take the latest
                    if len(swingStart0) == 2:
                        swingStart0 = max(swingStart0)
                    elif len(swingStart0) > 2:
                        swingStart00 = np.argmax(astp[swingStart0])
                        swingStart0 = swingStart0[swingStart00]
                    # get swing start
                    swingStart[i] = swingStart0
                    print(swingStart[i])
                    # get next valley
                    strideStart0 = iMinStp[swingStart0 < iMinStp]
                    print(strideStart0)
                    if not len(strideStart0):
                        deleteStride = True
                    # require valley to be less than 1g
                    elif astp[strideStart0[0]] >= 9.81:
                        deleteStride = True
                    else:
                        # get next instant where astrx crossed 1g
                        crossG = iCrossG[iCrossG > strideStart0[0]]
                        print("crossG: ", crossG)
                        plt.plot(crossG, data[crossG], 'x')
                        if not len(crossG):
                            deleteStride = True
                        else:
                            crossG = crossG[0]
                            # require crossg be within 320 ms of strideStart0
                            if crossG - strideStart0[0] > 32:
                                deleteStride = True
                            else:
                                # interpolate between current crossg
                                # (immediately after) and previous to estimate
                                strideStart[i] = crossG
                                print(strideStart)
                if deleteStride:
                    swingStart = np.delete(swingStart, i)
                    strideStart = np.delete(strideStart, i)
                    iMinStr = np.delete(iMinStr, i)
                else:
                    i += 1
        if not len(strideStart):
            deleteBout = True
        if not deleteBout:
            # stride ends are stride starts without first
            print("strideStart: ", strideStart)
            plt.plot(strideStart, data[[int(x) for x in strideStart]], 'o')
            plt.show()
            strideEnd = strideStart
            strideStart = np.delete(strideStart, len(strideStart)-1)#strideStart[len(strideStart)] = 0
            strideEnd = np.delete(strideEnd, 0)
            # FC before first swing start not identified, delete
            swingStart = np.delete(swingStart, 0)
            # get stride endpoints and check times
            nStrides = len(strideStart)
            print(nStrides)
            eventsStrideStart = np.zeros(nStrides)
            eventsStrideEnd = np.zeros(nStrides)
            eventsSwingStart = np.zeros(nStrides)
            eventsStrideTime = np.zeros(nStrides)
            eventsDutyFactor = np.zeros(nStrides)
            i = 0
            while i <= nStrides:
                deleteStride = False
                # get stride time
                print("strideEnd: ", strideEnd)
                print("strideStart: ", strideStart)
                strideTime0 = strideEnd[i] - strideStart[i]
                print("strideTime0: ", strideTime0)
                # duty factor
                dutyFactor0 = (swingStart[i] - strideStart[i]) / strideTime0
                print("dutyFactor0: ", dutyFactor0)
                # verify stride time / duty factor within constraints
                if strideTime0 > maxStrideTime or strideTime0 < minStrideTime:
                    deleteStride = True
                elif dutyFactor0 > maxDutyFactor or dutyFactor0 < minDutyFactor:
                    deleteStride = True
                if deleteStride:
                    print("DELETING STRIDE")
                    # delete the stride
                    strideEnd = np.delete(strideEnd, i, None)
                    strideStart = np.delete(strideStart, i, None)
                    swingStart = np.delete(swingStart, i, None)
                    nStrides -= 1
                    eventsStrideStart = np.delete(eventsStrideStart, i, None)
                    eventsStrideEnd = np.delete(eventsStrideEnd, i, None)
                    eventsStrideTime = np.delete(eventsStrideTime, i, None)
                    eventsSwingStart = np.delete(eventsSwingStart, i, None)
                    eventsDutyFactor = np.delete(eventsDutyFactor, i, None)
                else:
                    eventsStrideStart[i] = strideStart[i]
                    eventsStrideEnd[i] = strideEnd[i]
                    eventsStrideTime[i] = strideTime0
                    eventsSwingStart[i] = swingStart[i]
                    eventsDutyFactor[i] = dutyFactor0
                    i += 1
    return deleteBout, eventsStrideStart, eventsSwingStart, eventsStrideTime, eventsDutyFactor




if __name__ == "__main__":
    for subjectNum in [x for x in range(25, 26) if x not in [13, 20, 22, 46, 47, 48]]:
        goodSubjects = open("../../Utils/goodTrials",
                            "r").read()
        if "," + str(subjectNum) + "," in goodSubjects:
            subjectDir = "../../AlignedZeroedData/TF_{}".format(str(subjectNum).zfill(2))
            subjectDict = {}
            for file in os.listdir(subjectDir)[3:4]:
                print(file)
                # load data
                trialNum = int(file.split(".")[0].split("-")[-1])
                subjectDict[str(trialNum).zfill(4)] = {"left": {}, "right": {}, "chest": {}}
                print("{}: {}".format(subjectNum, trialNum))
                data = pd.read_csv(os.path.join(subjectDir, file), usecols=["AccZpocket"])
                firstNonZeroIdx = data.ne(0).idxmax()[0]
                data = data.iloc[firstNonZeroIdx:, :].to_numpy().flatten()
                _, IC, TO, strideTime, dutyFactor = gurchiek(data, 70, 225, 0.2, 0.4, 1)
                print(IC)

