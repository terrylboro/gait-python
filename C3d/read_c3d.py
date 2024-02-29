import numpy as np
import pyc3dserver as c3d
import matplotlib.pyplot as plt

# Get the COM object of C3Dserver
itf = c3d.c3dserver()

# Open a C3D file
ret = c3d.open_c3d(itf, "15_CU_synch_testing04.c3d")

# For the information of all analogs(excluding or including forces/moments)
# dict_analogs = c3d.get_dict_analogs(itf)

start_fr = itf.GetVideoFrame(0)
end_fr = itf.GetVideoFrame(1)
## Mapping the sensor data to values ########
# Sensor 1 Acc.X = 93
# Sensor 1 Acc.Y = 94
# Sensor 1 Acc.Z = 95
# Sensor 1 Gyro.X = 96
# Sensor 1 Gyro.Y = 97
# Sensor 1 Gyro.Z = 98
# Sensor 2 Acc.X = 165
# Sensor 2 Acc.Y = 166
# Sensor 2 Acc.Z = 167
# Sensor 2 Gyro.X = 168
# Sensor 2 Gyro.Y = 169
# Sensor 2 Gyro.Z = 170

sensor1Range = range(93, 98+1)
sensor2Range = range(165, 170+1)

sensor_arr = np.empty((end_fr * 20, 12))

for sig_idx in sensor1Range:
    data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    sensor_arr[:, sig_idx - 93] = data
    # plt.plot(data)

for sig_idx in sensor2Range:
    data = np.asarray(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    sensor_arr[:, sig_idx - 165 + 6] = data
    # plt.plot(data)

np.savetxt("synch04.csv", sensor_arr, delimiter=",")

# y = json.dumps(dict_analogs)
# print(y['DATA'])

# Close the C3D file from C3Dserver
ret = c3d.close_c3d(itf)
