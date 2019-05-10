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
            else:
                columns = 'time,cpu_count,cpu_type,memory_total,comment\n'
            file.write(columns)
            file.close()

        if f == 'machine_config':
            config_file = open(f_path)
            state['old_configuration'] = config_file.readlines()
            config_file.close()
        state[f] = open(f_path, 'a')

def write_configuration(state, time, cpu_type, cpu_count, mem_total, comment):
    line = '%d,%s,%d,%d,%s\n'%(time, cpu_type, cpu_count, mem_total, comment)
    state['machine_config'].write(line)
    state['machine_config'].flush()

def write_utilization(state, time, cpu, mem, ing, eg):
    out = '%d,%f,%f,%d,%d\n'%(time, cpu, mem, ing, eg)
    state['trace'].write(out)