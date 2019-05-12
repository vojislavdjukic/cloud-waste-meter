from __future__ import print_function

import os
import pandas as pd

def find_configuration(timestamp, configurations):
    number_of_configurations = len(configurations.index)
    if timestamp <= configurations.at[0, 'time']:
        return configurations.iloc[[0]]
    if timestamp >= configurations.at[number_of_configurations-1, 'time']:
        return configurations.iloc[[number_of_configurations-1]]

def create_report(step, trace_path, machine_config_path):
    trace_df = pd.read_csv(trace_path)
    machine_config_df = pd.read_csv(machine_config_path)

    res = find_configuration(trace_df['time'][0], machine_config_df)
    print(res)