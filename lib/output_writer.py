from __future__ import print_function

import os

from .util import cmd


def initialize_output_writer(state):
    home_dir = os.path.expanduser(state['params']['home_dir'])
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
    if not os.path.isdir(home_dir):
        raise Exception('File passed as home directory')

    files = ['trace', 'machine_config']
    for f in files:
        f_path = home_dir+f+'.log'
        if state['params']['overwrite_logs'] or not os.path.exists(f_path):
            file = open(f_path, 'w')
            #write header
            if f == 'trace':
                columns = 'time,cpu,memory,ingress,egress\n'
            elif f == 'machine_config':
                columns = 'time,cpu_count,memory_total,cpu_type,instance_type,region,comment\n'
            file.write(columns)
            file.close()

        if f == 'machine_config':
            config_file = open(f_path)
            state['old_configuration'] = config_file.readlines()
            config_file.close()
        state[f] = open(f_path, 'a')


def write_configuration(state, time, cpu_count, mem_total, cpu_type, instance_type, region, comment):
    line = '%d,%d,%d,%s,%s,%s,%s\n'%(time, cpu_count, mem_total, cpu_type, instance_type, region, comment)
    state['machine_config'].write(line)
    state['machine_config'].flush()


def write_utilization(state, time, cpu, mem, ing, eg):
    out = '%d,%f,%f,%d,%d\n'%(time, cpu, mem, ing, eg)
    state['trace'].write(out)


def initialize_report_writer(state):
    home_dir = os.path.expanduser(state['params']['home_dir'])

    if not os.path.isdir(home_dir):
        raise Exception('File passed as home directory')

    f_path = home_dir+'report.log'
    if state['params']['overwrite_logs'] or not os.path.exists(f_path):
        file = open(f_path, 'w')
        #write header
        columns = 'analysis_time,from_time,to_time,max_cpu,avg_cpu,max_memory,avg_memory,max_band,avg_band'
        columns += ',current_instance,recommended_instance,current_cost,recommended_cost,potential_saving,waste'
        file.write(columns)
        file.close()

    state['report'] = open(f_path, 'a')


def write_report(
    analysis_time,from_time,to_time,max_cpu,avg_cpu,max_memory,avg_memory,max_band,avg_band,
    current_instance,recommended_instance,current_cost,recommended_cost,potential_saving,waste
):
    out = '%d,%d,%d,%f,%f,%d,%f,%f,%f,%s,%s,%f,%f,%f,%f\n'%(
        analysis_time,from_time,to_time,max_cpu,avg_cpu,max_memory,avg_memory,max_band,avg_band,
        current_instance,recommended_instance,current_cost,recommended_cost,potential_saving,waste
    )
    state['report'].write(line)
    state['report'].flush()
