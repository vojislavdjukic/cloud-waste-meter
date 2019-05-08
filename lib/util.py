from __future__ import print_function
import subprocess
import os


def cmd(command):
    return subprocess.check_output(command, shell=True).decode('utf-8')


def initialize_output_folder(state, cmd_args):
    home_dir = os.path.expanduser(cmd_args.home_dir)
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
    if not os.path.isdir(home_dir):
        raise Exception('File passed as home directory')

    files = ['trace', 'machine_config']
    for f in files:
        f_path = home_dir+f+'.log'
        if cmd_args.overwrite_logs or not os.path.exists(f_path):
            file = open(f_path, 'w')
            #write header
            if f == 'trace':
                columns = 'time,cpu,memory,ingress,egress\n'
                file.write(columns)
            file.close()
        state[f] = open(f_path, 'a')


def store_machine_configuration(state):
    cpu_total = 'cpu_total:%s\n'%(state['cpu_total'])
    cpu_type = 'cpu_type:%s\n'%(state['cpu_type'])
    mem_total = 'mem_total:%s\n'%(state['mem_total'])

    state['machine_config'].write(cpu_total)
    state['machine_config'].write(cpu_type)
    state['machine_config'].write(mem_total)
    
    state['machine_config'].close()