from __future__ import print_function

import os
import pandas as pd

def find_configuration(timestamp, configurations):
    number_of_configurations = len(configurations.index)
    if timestamp <= configurations.at[0, 'time']:
        return configurations.iloc[[0]]
    if timestamp >= configurations.at[number_of_configurations-1, 'time']:
        return configurations.iloc[[number_of_configurations-1]]

def find_configurations(start_time, end_time, configurations):
    events = []
    events.append((start_time,-1))
    events.append((end_time,-1))

    times = configurations['time'].tolist()
    for i, t in enumerate(times):
        events.append((t, i))

    events.append((0, 0))

    events = sorted(events, key = lambda x: x[0])

    i = events.index((start_time,-1))

    map(lambda x: if x[1] , events[:-1])

    [ (events[i]) for i in range(len(events)-1)]

    while events[i] != (end_time,-1):

    return events

def create_report(step, trace_path, machine_config_path):
    trace_df = pd.read_csv(trace_path)
    machine_config_df = pd.read_csv(machine_config_path)

    time_start = trace_df.at[0, 'time']
    number_of_logs = len(trace_df.index)
    time_end = trace_df.at[number_of_logs-1, 'time']

    res = find_configurations(time_start, time_end, machine_config_df)
    print(res)