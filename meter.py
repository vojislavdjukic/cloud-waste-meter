from __future__ import print_function

import os
import subprocess
from time import sleep

state = {}


def cmd(command):
    return subprocess.check_output(command, shell=True).decode('utf-8')


def parse_cpu(stat_out, old_measurements):
    cmd = stat_out.split()

    mapping = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice']
    f = lambda cmd,field: int(cmd[mapping.index(field)+1])

    idle = f(cmd,'idle') + f(cmd,'iowait')
    non_idle = f(cmd,'user') + f(cmd,'nice') + f(cmd,'system') + f(cmd,'irq') + f(cmd,'softirq') + f(cmd,'steal')

    if old_measurements is not None and old_measurements[0] is not None:
        old_idle = old_measurements[0]
        old_non_idle = old_measurements[1]
        total = idle + non_idle
        old_total = old_idle + old_non_idle
        totald = float(total-old_total)
        idled = float(idle-old_idle)

        if totald != 0:
            cpu = (totald - idled)/totald
        else:
            cpu = 0

        sleep(0.05)

        return (cpu, idle, non_idle)
    else:
        return (0, idle, non_idle)


def measure_cpu():
    stat_out = cmd('cat /proc/stat')
    res = parse_cpu(stat_out, (state['cpu'][0], state['cpu'][1]))
    state['cpu'] = (res[1],res[2])
    return res[0]

def measure_network():
    dev_out = cmd('cat /proc/net/dev')
    dev_out = dev_out.split('\n')
    for line in dev_out[2:]:
        sp = line.split()
        if sp[0][:-1]==state['interface_name']:
            ingress = float(sp[1])
            egress = float(sp[9])
            break
    diff_ing = ingress - state['total_ingress']
    diff_eg = egress - state['total_egress']
    state['total_ingress'] = ingress
    state['total_egress'] = egress
    return diff_ing, diff_eg

def init_state():
    #initialize cpu measurements
    state['cpu'] = (None, None)
    measure_cpu()
    state['cpu_total'] = int(cmd("cat /proc/cpuinfo | awk '/^processor/{print $3}' | wc -l").strip())

    #initialize memory measurement
    out = cmd('cat /proc/meminfo')
    out = out.split()
    state['mem_total'] = float(out[1])

    #initialize network measurement
    out = cmd('nmcli device status').split('\n')
    for line in out[1:]:
        sp = line.split()
        if sp[1]=='ethernet':
            state['interface_name'] = sp[0]
            break
    state['total_ingress'] = 0
    state['total_egress'] = 0
    measure_network()


def measure_memory():
    out = cmd('cat /proc/meminfo')
    out = out.split()
    mem = float(out[7])
    mem_per = (state['mem_total'] - mem)/state['mem_total']
    return mem_per


def main():
    init_state()

    while True:
        cpu = measure_cpu()
        mem = measure_memory()
        ing, eg = measure_network()
        print('CPU: ', cpu, 'Memory:', mem)
        print('Ingress: ', ing, 'Egress:', eg)
        sleep(1)    

if __name__ == '__main__':
    main()
