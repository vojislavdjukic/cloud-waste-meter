from __future__ import print_function

import os
from time import sleep
from argparse import ArgumentParser

from lib.util import cmd
from lib.util import initialize_output_folder
from lib.util import store_machine_configuration
from lib.cpu_monitor import measure_cpu, initialize_cpu_monitor
from lib.memory_monitor import measure_memory, initialize_memory_monitor
from lib.network_monitor import measure_network, initialize_network_monitor

state = {}

parser = ArgumentParser()
parser.add_argument('-f', '--frequency', type=float, default=1.0,
    help='Frequency of measurements')
parser.add_argument('-home', '--home-dir', type=str, default='~/.wastemeter/',
    help='wastemeter home directory')


def init_state(home_dir):
    initialize_output_folder(state, home_dir)

    initialize_cpu_monitor(state)
    initialize_memory_monitor(state)
    initialize_network_monitor(state)

    store_machine_configuration(state)

def main():
    args = parser.parse_args()

    init_state(args.home_dir)

    while True:
        cpu = measure_cpu(state)
        mem = measure_memory(state)
        ing, eg = measure_network(state)
        print('CPU: ', cpu, 'Memory:', mem)
        print('Ingress: ', ing, 'Egress:', eg)
        sleep(args.frequency)


if __name__ == '__main__':
    main()
