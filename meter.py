from __future__ import print_function

import os
from time import sleep
from argparse import ArgumentParser
import time

from lib.util import cmd
from lib.util import initialize_output_folder
from lib.util import store_machine_configuration
from lib.cpu_monitor import measure_cpu, initialize_cpu_monitor
from lib.memory_monitor import measure_memory, initialize_memory_monitor
from lib.network_monitor import measure_network, initialize_network_monitor

state = {}

parser = ArgumentParser()
parser.add_argument('-f', '--frequency', type=float, default=1.0,
    help='Frequency of measurements in seconds')
parser.add_argument('-home', '--home-dir', type=str, default='~/.wastemeter/',
    help='wastemeter home directory')
parser.add_argument('-ol', '--overwrite-logs', action='store_true',
    help='Overwrite old logs files and create new logs')
parser.add_argument('-ff', '--flush-frequency', type=float, default=5.0,
    help='Flush frequency in seconds - how often to persist measurements on disk')


def init_state(cmd_args):
    initialize_output_folder(state, cmd_args)

    initialize_cpu_monitor(state)
    initialize_memory_monitor(state)
    initialize_network_monitor(state)

    store_machine_configuration(state)


def main():
    args = parser.parse_args()
    init_state(args)

    t_old = 0
    while True:
        t = int(round(time.time() * 1000))
        cpu = measure_cpu(state)
        mem = measure_memory(state)
        ing, eg = measure_network(state)
        out = '%d,%f,%f,%d,%d\n'%(t, cpu, mem, ing, eg)
        state['trace'].write(out)
        if t-t_old>args.flush_frequency*1000:
            state['trace'].flush()
            t_old = t
        sleep(args.frequency)


if __name__ == '__main__':
    main()
