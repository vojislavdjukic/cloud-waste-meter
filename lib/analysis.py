from __future__ import print_function

import os
import pandas as pd
import requests
import matplotlib.pyplot as plt

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

    configurations = find_configurations(time_start, time_end, machine_config_df)
    
    pricing = load_aws_pricing()

    #calculate the cost of execution
    total_cost = 0
    total_execution_time = 0
    for r in configurations:
        execution_time = (r[1]-r[0])/1000. #in seconds
        instance_type = r[2].at[0, 'instance_type']
        region = r[2].at[0, 'region']
        mt = pricing[region][instance_type]
        
        total_cost += mt['cost']*execution_time/3600.
        total_execution_time = execution_time

    print('Total execution time: %.2f seconds = %.2f days'%(total_execution_time, total_execution_time/(3600*24)))
    print('Total cost: %.2f$'%total_cost)

    time = trace_df['time'].tolist()
    start_time = time[0]
    time = map(lambda x: (x-start_time)/1000., time)

    cpu = trace_df['cpu'].tolist()[1:]
    memory = trace_df['memory'].tolist()[1:]

    time_intervals = [(time[i+1]-time[i]) for i in range(len(time)-1)]
    time = time[1:]

    ingress = trace_df['ingress'].tolist()[1:]
    ingress = [ingress[i]/(1000000*time_intervals[i]) for i in range(len(time))] #Mbps
    egress = trace_df['egress'].tolist()[1:]
    egress = [egress[i]/(1000000*time_intervals[i]) for i in range(len(time))] #Mbps

    fig = plt.figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    ax1.plot(time, cpu)
    ax1.set_ylabel('CPU (%)')
    ax1.get_xaxis().set_visible(False)

    ax2.plot(time, memory)
    ax2.set_ylabel('Memory (%)')
    ax2.get_xaxis().set_visible(False)

    ax3.plot(time, ingress, time, egress)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Network bandwidth (Mbps)')

    plt.show()
    



    
