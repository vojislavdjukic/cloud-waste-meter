from __future__ import print_function

import os
import time
import sys
import re

from .util import cmd
from .output_writer import write_configuration


machine_type_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'

#python 2 vs python 3 http request
if sys.version_info[0] < 3:
    def fetch_instance_type():
        try:
            import urllib2
            output = urllib2.urlopen(machine_type_url, timeout = 1).read()
            instance_type = re.search(r'"instanceType" : "(.+)"', output).group(1)
            region = re.search(r'"region" : "(.+)"', output).group(1)
            return instance_type, region
        except:
            return None, None
else:
    def fetch_instance_type():
        try:
            import urllib.request
            output = urllib.request.urlopen(machine_type_url).read()
            instance_type = re.search(r'"instanceType" : "(.+)"', output).group(1)
            region = re.search(r'"region" : "(.+)"', output).group(1)
            return instance_type, region
        except:
            return None, None

def get_new_configuration():
    #CPU information - number of cores and CPU type
    cpu_count = int(cmd("cat /proc/cpuinfo | awk '/^processor/{print $3}' | wc -l").strip())
    cpu_type = cmd("cat /proc/cpuinfo | awk '/^model name/{print; exit}'").split(":")[1].strip()
    
    #total memory
    out = cmd('cat /proc/meminfo')
    out = out.split()
    mem_total = int(out[1])

    return (cpu_count, mem_total, cpu_type)


def initialize_configuration_monitor(state):
    home_dir = os.path.expanduser(state['params']['home_dir'])
    config_file_path = home_dir + 'machine_config.log'
    lines = state['old_configuration']

    #if there are previous configurations
    if len(lines)>1:
        split = lines[-1][:-1].split(',')
        old_config = (int(split[1]), int(split[2]), split[3], split[4])
    else:
        old_config = (0, 0, 0, '')

    #get new configuration and see if there are any differences
    cpu_count, mem_total, cpu_type = get_new_configuration()

    instance_type, region = fetch_instance_type()
    if instance_type is None:
        instance_type = 'unknown'
        region = 'unknown'
    
    new_config = (cpu_count, mem_total, cpu_type, instance_type)
    
    if old_config != new_config:
        t = int(round(time.time() * 1000))
        write_configuration(state, t, cpu_count, mem_total, cpu_type, instance_type, region, '')

    state['cpu_type'] = cpu_type
    state['cpu_count'] = cpu_count
    state['mem_total'] = mem_total
    state['instance_type'] = instance_type
    state['region'] = region


def update_machine_configuration(state, timestamp):
    old_cpu_type = state['cpu_type']
    old_cpu_count = state['cpu_count']
    old_mem_total = state['mem_total']
    cpu_count, mem_total, cpu_type = get_new_configuration()
    if cpu_type != old_cpu_type or cpu_count != old_cpu_count or mem_total != old_mem_total:
        write_configuration(state, timestamp, cpu_type, cpu_count, mem_total, state['instance_type'], '')
    
