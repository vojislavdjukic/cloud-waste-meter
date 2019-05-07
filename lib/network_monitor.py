from __future__ import print_function

from util import cmd


def measure_network(state):
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


def initialize_network_monitor(state):
    out = cmd('nmcli device status').split('\n')
    for line in out[1:]:
        sp = line.split()
        if sp[1]=='ethernet':
            state['interface_name'] = sp[0]
            break
    state['total_ingress'] = 0
    state['total_egress'] = 0
    measure_network(state)