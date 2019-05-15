from __future__ import print_function

import os
import pandas as pd
import requests

from .util import load_aws_pricing

def find_configuration(timestamp, configurations):
    number_of_configurations = len(configurations.index)
    if timestamp <= configurations.at[0, 'time']:
        return configurations.iloc[[0]]
    if timestamp >= configurations.at[number_of_configurations-1, 'time']:
        return configurations.iloc[[number_of_configurations-1]]

def find_configurations(start_time, end_time, configurations):
    events = []
    st = (start_time,-1)
    et = (end_time,-1)
    events.append(st)
    events.append(et)
    times = configurations['time'].tolist()
    for i, t in enumerate(times):
        events.append((t, i))
    events.append((0, 0))
    events = sorted(events, key = lambda x: x[0])

    si = events.index(st)
    ei = events.index(et)
    res = [ (events[i-1][0], events[i][0], events[i-1][1]) for i in range(1,len(events))]

    for i in range(len(res)):
        if res[i][2] == -1:
            res[i] = (res[i][0], res[i][1], res[i-1][2])

    res = res[si:ei+1]
    for i in range(len(res)):
        res[i] = (res[i][0], res[i][1], configurations.iloc[[res[i][2]]])
    return res

def create_report(step, trace_path, machine_config_path):
    trace_df = pd.read_csv(trace_path)
    machine_config_df = pd.read_csv(machine_config_path)

    time_start = trace_df.at[0, 'time']
    number_of_logs = len(trace_df.index)
    time_end = trace_df.at[number_of_logs-1, 'time']

    res = find_configurations(time_start, time_end, machine_config_df)
    
    pricing = load_aws_pricing()

    #calculate the cost of execution
    for r in res:
        print(r)
        execution_time = (r[1]-r[0])/1000. #in seconds
        instance_type = r[2].at[0, 'instance_type']
        region = r[2].at[0, 'region']
        mt = pricing[region][instance_type]
        print(mt)
        print(execution_time/3600.)
        print('Total execution cost is %.2f$'%(mt['cost']*execution_time/3600.))


    



    
