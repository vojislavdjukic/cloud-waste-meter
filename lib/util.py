from __future__ import print_function
import subprocess
import os

def cmd(command):
    return subprocess.check_output(command, shell=True).decode('utf-8')


def initialize_output_folder(state, home_dir):
    home_dir = os.path.expanduser(home_dir)
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
    if not os.path.isdir(home_dir):
        raise Exception('File passed as home directory')

    files = ['trace', 'machine_config']
    for f in files:
        f_path = home_dir+f+'.log'
        if not os.path.exists(f_path):
            file = open(f_path, 'w')
            #write header
            if f == 'trace':
                columns = 'time,cpu,memory,ingress,egress\n'
                file.write(columns)
            file.close()
        state[f] = open(f_path, 'a')

def store_machine_configuration(state):
    pass