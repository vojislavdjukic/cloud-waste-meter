from __future__ import print_function

import os
from time import sleep
from argparse import ArgumentParser
import time

from lib.output_writer import initialize_output_writer, write_utilization

from lib.configuration_monitor import initialize_configuration_monitor, update_machine_configuration

from lib.cpu_monitor import measure_cpu, initialize_cpu_monitor
from lib.memory_monitor import measure_memory, initialize_memory_monitor
from lib.network_monitor import measure_network, initialize_network_monitor

state = {}
state['params'] = {}

# http://169.254.169.254/latest/meta-data/instance-type

parser = ArgumentParser()
parser.add_argument('-f', '--frequency', type=float, default=1.0,
    help='Frequency of measurements in seconds')
parser.add_argument('-home', '--home-dir', type=str, default='~/.wastemeter/',
    help='wastemeter home directory')
parser.add_argument('-ol', '--overwrite-logs', action='store_true',
    help='Overwrite old logs files and create new logs')
parser.add_argument('-ff', '--flush-frequency', type=float, default=5.0,
    help='Flush frequency in seconds - how often to persist measurements on disk')

def store_params(args):
    state['params']['frequency'] = args.frequency
    state['params']['home_dir'] = args.home_dir
    state['params']['overwrite_logs'] = args.overwrite_logs
    state['params']['flush_frequency'] = args.flush_frequency

def init_state():
    initialize_output_writer(state)
    initialize_configuration_monitor(state)

    initialize_cpu_monitor(state)
    initialize_memory_monitor(state)
    initialize_network_monitor(state)


def main():
    args = parser.parse_args()
    store_params(args)
    init_state()

    t_old = 0
    while True:
        t = int(round(time.time() * 1000))
        cpu = measure_cpu(state)
        mem = measure_memory(state)
        ing, eg = measure_network(state)
        write_utilization(state, t, cpu, mem, ing, eg)
        if t-t_old>args.flush_frequency*1000:
            state['trace'].flush()
            t_old = t
            update_machine_configuration(state, t)
        sleep(args.frequency)


if __name__ == '__main__':
    main()
