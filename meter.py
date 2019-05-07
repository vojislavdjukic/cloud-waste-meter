from __future__ import print_function

import os
from time import sleep
from lib.util import cmd
from lib.cpu_monitor import measure_cpu, initialize_cpu_monitor
from lib.memory_monitor import measure_memory, initialize_memory_monitor
from lib.network_monitor import measure_network, initialize_network_monitor

state = {}


def init_state():
    initialize_cpu_monitor(state)
    initialize_memory_monitor(state)
    initialize_network_monitor(state)


def main():
    init_state()

    while True:
        cpu = measure_cpu(state)
        mem = measure_memory(state)
        ing, eg = measure_network(state)
        print('CPU: ', cpu, 'Memory:', mem)
        print('Ingress: ', ing, 'Egress:', eg)
        sleep(1)    


if __name__ == '__main__':
    main()
