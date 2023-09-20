import numpy as np
import pandas as pd
import os

def save_gait_events(LHC, RHC, LTO, RTO, method, subject, trial_num, side):
    event_array = np.zeros((max(len(LHC), len(RHC), len(LTO), len(RTO)), 4), dtype=np.int64)
    gait_events = [LHC, RHC, LTO, RTO]
    for i in range(0, 4):
        event_array[:len(gait_events[i]), i] = gait_events[i]
    event_array_df = pd.DataFrame(event_array)
    event_array_df.insert(0, "Trial", trial_num)
    event_array_df.columns = ['Trial', 'LHC', 'RHC', 'LTO', 'RTO']
    # event_array_df.to_csv(os.getcwd() + "/" + subject + "/" + subject.lower() + "-events-" + str(trial_num) + "-" + side + ".csv", index_label="Index")
    event_array_df.to_csv("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Processing/" + method + "/" + subject
                          + "/" + subject.lower() + "-events-" + str(trial_num) + "-" + side + ".csv",
                          index_label="Index")
