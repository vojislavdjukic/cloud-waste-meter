from __future__ import print_function

import os
import time

from .util import cmd
from .output_writer import write_configuration

#'time,cpu_count,cpu_type,memory_total,comment\n'
def get_new_configuration():
    #CPU information - number of cores and CPU type
    cpu_count = int(cmd("cat /proc/cpuinfo | awk '/^processor/{print $3}' | wc -l").strip())
    cpu_type = cmd("cat /proc/cpuinfo | awk '/^model name/{print; exit}'").split(":")[1].strip()
    
    #total memory
    out = cmd('cat /proc/meminfo')
    out = out.split()
    mem_total = int(out[1])

    return (cpu_type, cpu_count, mem_total)

def initialize_configuration_monitor(state):
    home_dir = os.path.expanduser(state['params']['home_dir'])
    config_file_path = home_dir + 'machine_config.log'
    config_file = open(config_file_path)
    #columns = 'time,cpu_count,cpu_type,memory_total,comment\n'
    lines = config_file.readlines()
    config_file.close()

    #if there are previous configurations
    if len(lines)>1:
        split = lines[-1][:-1].split(',')
        old_cpu_type = split[1]
        old_cpu_count = int(split[2])
        old_mem_total = int(split[3])
    else:
        old_cpu_type = 0
        old_cpu_count = 0
        old_mem_total = 0

    #get new configuration and see if there are any differences
    cpu_type, cpu_count, mem_total = get_new_configuration()
    if cpu_type != old_cpu_type or cpu_count != old_cpu_count or mem_total != old_mem_total:
        t = int(round(time.time() * 1000))
        write_configuration(state, t, cpu_type, cpu_count, mem_total, '')

    state['cpu_type'] = cpu_type
    state['cpu_count'] = cpu_count
    state['mem_total'] = mem_total

def update_machine_configuration(state, timestamp):
    old_cpu_type = state['cpu_type']
    old_cpu_count = state['cpu_count']
    old_mem_total = state['mem_total']
    cpu_type, cpu_count, mem_total = get_new_configuration()
    if cpu_type != old_cpu_type or cpu_count != old_cpu_count or mem_total != old_mem_total:
        write_configuration(state, timestamp, cpu_type, cpu_count, mem_total, '')
    
