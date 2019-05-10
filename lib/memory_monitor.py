from __future__ import print_function

from .util import cmd


def measure_memory(state):
    out = cmd('cat /proc/meminfo')
    out = out.split()
    mem = float(out[7])
    mem_per = (state['mem_total'] - mem)/state['mem_total']
    return mem_per


def initialize_memory_monitor(state):
    pass
