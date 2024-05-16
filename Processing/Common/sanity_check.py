import pandas as pd
import numpy as np

def sanity_check(ic_peaks, fc_peaks):
    """ Heavily influenced by GaitPy """
    # import pandas as pd
    # import numpy as np

    # Parameters
    gait_cycle_forward_ic = 2.25  # maximum allowable time (seconds) between initial contact of same foot
    loading_forward_fc = gait_cycle_forward_ic * 0.2  # maximum time (seconds) for loading phase
    stance_forward_fc = (gait_cycle_forward_ic / 2) + loading_forward_fc  # maximum time (seconds) for stance phase

    # Optimization 1: ---Loading Response--- Each IC requires 1 forward FC within 0.225 seconds (opposite foot toe off)
    #              2: ---Stance Phase--- Each IC requires atleast 2 forward FC's within 1.35 second (2nd FC is current IC's matching FC)

    optimized_gait = pd.DataFrame([])
    for i in range(0, len(ic_peaks)):
        current_ic = ic_peaks[i]
        loading_forward_max = current_ic + (loading_forward_fc * 100.)
        stance_forward_max = current_ic + (stance_forward_fc * 100.)

        loading_forward_fcs = fc_peaks[(fc_peaks > current_ic) & (fc_peaks < loading_forward_max)]
        stance_forward_fcs = fc_peaks[(fc_peaks > current_ic) & (fc_peaks < stance_forward_max)]

        if len(loading_forward_fcs) == 1 and len(stance_forward_fcs) >= 2:
            icfc = pd.DataFrame({'IC': [current_ic], 'FC': [stance_forward_fcs[1]], 'FC_opp_foot': [stance_forward_fcs[0]], 'Gait_Cycle': [0]},
                                columns=['IC', 'FC', 'FC_opp_foot', 'Gait_Cycle'])
            optimized_gait = optimized_gait.append(icfc)

    # Optimization 3: ---Gait Cycles--- Each ic requires atleast 2 ics within 2.25 seconds after
    for i in range(0, len(optimized_gait) - 2):
        current_ic = optimized_gait.IC.iloc[i] / 100.
        post_ic = optimized_gait.IC.iloc[i + 1] / 100.
        post_2_ic = optimized_gait.IC.iloc[i + 2] / 100.

        interval_1 = abs(post_ic - current_ic)
        interval_2 = abs(post_2_ic - current_ic)

        if interval_1 <= gait_cycle_forward_ic and interval_2 <= gait_cycle_forward_ic:
            optimized_gait.Gait_Cycle.iloc[i] = 1

    return optimized_gait
