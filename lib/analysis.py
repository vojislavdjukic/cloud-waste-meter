from __future__ import print_function

import os
import pandas as pd
import requests
import matplotlib.pyplot as plt

from .util import load_aws_pricing

def load_data(state):
    trace_path = state['params']['trace_file']
    machine_config_path = state['params']['machine_config_file']

    #load traces
    trace = pd.read_csv(trace_path)
    configurations = pd.read_csv(machine_config_path)

    #extract start and end time of the experiment
    time_start = trace.at[0, 'time']
    number_of_logs = len(trace.index)
    time_end = trace.at[number_of_logs-1, 'time']

    #normalize time
    trace['time'] = trace['time'] - time_start
    configurations['time'] = configurations.apply(lambda x: max(0, x['time']-time_start), axis = 1)

    time_end -= time_start 

    return time_end, trace, configurations

def find_cheapest_instance(cpu, memory, network, region, state):
    pricing = state['pricing']['region']

def find_configurations(time_start, time_end, configurations, state):
    assert time_start < time_end

    config_index = 0
    while time_start > configurations.at[config_index, 'time']:
        config_index += 1
    config_index = max(0, config_index-1)

    configurations['memory_total'] = configurations['memory_total']/1000000.

    configs = []
    current_time = time_start
    while config_index < len(configurations)-1 and time_end > configurations.at[config_index, 'time']:
        configs.append((
            current_time,
            configurations.at[config_index+1, 'time'],
            configurations.iloc[[config_index]]
        ))
        current_time = configurations.at[config_index+1, 'time']
        config_index += 1

    config_index = max(0, config_index-1)
    configs.append((
        current_time,
        time_end,
        configurations.iloc[[config_index]]
    ))

    #process configs
    result = []
    for config in configs:
        instance_type = config[2].at[0,'instance_type']
        region = config[2].at[0,'region']        
        if region == 'unknown' or instance_type == 'unknown':
            region = "us-west-2"
            instance = find_cheapest_instance(cpu, memory, network, region, state)
        else:
            instance = state['pricing'][region][instance_type]
        mc = {
            'cpu': config[2].at[0,'cpu_count'],
            'memory': config[2].at[0,'memory_total'],
            'instance_type': instance_type,
            'region': region,
            'instance_cpu': instance['cpu'],
            'instance_memory': instance['memory'],
            'instance_network': instance['network'],
            'cost': instance['cost']
        }
        result.append((config[0], config[1], mc))
    return result


def calculate_cost(configurations):
    #calculate the cost of execution
    total_cost = 0
    total_execution_time = 0
    for r in configurations:
        execution_time = (r[1]-r[0])/1000. #in seconds
        total_cost += r[2]['cost']*execution_time/3600.
        total_execution_time += execution_time
    return total_cost

def plot_underutilized(trace_df, configurations):
    time = trace_df['time'].tolist()
    time_start = time[0]
    time = list(map(lambda x: (x-time_start)/1000., time))

    time_intervals = [(time[i+1]-time[i]) for i in range(len(time)-1)]
    time = time[1:]

    #calculate configuration index
    config_index = 0
    target_config = [0]*len(time)
    for i in range(len(time)):
        target_config[i] = config_index 
        if time[i] > configurations[config_index][1]:
            config_index += 1

    cpu = trace_df['cpu'].tolist()[1:]
    cpu = [configurations[target_config[i]][2]['cpu'] - cpu[i] for i in range(len(target_config))]

    memory = trace_df['memory'].tolist()[1:]
    memory = [configurations[target_config[i]][2]['memory'] * (1-memory[i]) for i in range(len(target_config))]

    ingress = trace_df['ingress'].tolist()[1:]
    ingress = [ingress[i]/(1000000000*time_intervals[i]) for i in range(len(time))] #Gbps
    ingress = [configurations[target_config[i]][2]['instance_network'] * (1-ingress[i]) for i in range(len(target_config))]

    egress = trace_df['egress'].tolist()[1:]
    egress = [egress[i]/(1000000000*time_intervals[i]) for i in range(len(time))] #Gbps
    egress = [configurations[target_config[i]][2]['instance_network'] * (1-egress[i]) for i in range(len(target_config))]

    fig = plt.figure()
    ax1 = fig.add_subplot(411)
    ax2 = fig.add_subplot(412)
    ax3 = fig.add_subplot(413)
    ax4 = fig.add_subplot(414)

    #ax1.plot(time, cpu)
    ax1.fill_between(time, 0, cpu, hatch='//')
    ax1.set_ylabel('CPU (%)')
    ax1.get_xaxis().set_visible(False)

    ax2.fill_between(time, 0, memory, hatch='//')
    ax2.set_ylabel('Memory (GB)')
    ax2.get_xaxis().set_visible(False)

    ax3.fill_between(time, 0, ingress, hatch='//')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Ingress bandwidth (Gbps)')

    ax4.fill_between( time, 0, egress, hatch='//')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Egress bandwidth (Gbps)')

    plt.show()


def create_report(state):
    state['pricing'] = load_aws_pricing()
    time_end, trace, configurations = load_data(state)
    print('Total execution time: %.2f seconds = %.2f days'%(time_end, time_end/(1000*3600*24)))

    #find active configurations during the experiment
    configurations = find_configurations(0, time_end, configurations, state)
    
    total_cost = calculate_cost(configurations)
    print('Total cost: %.2f$'%total_cost)

    if state['params']['plot']:
        plot_underutilized(trace, configurations)
   
 