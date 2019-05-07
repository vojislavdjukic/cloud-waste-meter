from __future__ import print_function

from util import cmd


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

        return (cpu, idle, non_idle)
    else:
        return (0, idle, non_idle)


def measure_cpu(state):
    stat_out = cmd('cat /proc/stat')
    res = parse_cpu(stat_out, (state['cpu'][0], state['cpu'][1]))
    state['cpu'] = (res[1],res[2])
    return res[0]


def initialize_cpu_monitor(state):
    state['cpu'] = (None, None)
    measure_cpu(state)
    state['cpu_total'] = int(cmd("cat /proc/cpuinfo | awk '/^processor/{print $3}' | wc -l").strip())