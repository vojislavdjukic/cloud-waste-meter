from __future__ import print_function

import os
from argparse import ArgumentParser

from lib.output_writer import initialize_report_writer, write_report
from lib.analysis import create_report

state = {}
state['params'] = {}


parser = ArgumentParser()
parser.add_argument('-home', '--home-dir', type=str, default='~/.wastemeter/',
    help='wastemeter home directory')
parser.add_argument('-tf', '--trace-file', type=str, default='',
    help='Path to the trace file. If not set, the file is assumed to be in the home folder.')
parser.add_argument('-mcf', '--machine-config-file', type=str, default='',
    help='Path to the machine configuration file. If not set, the file is assumed to be in the home folder.')
parser.add_argument('-ol', '--overwrite-logs', action='store_true',
    help='Overwrite old logs files and create new logs')
parser.add_argument('-s', '--step', type=float, default=3600,
    help='Report step in seconds')


def store_params(args):
    state['params']['home_dir'] = os.path.expanduser(args.home_dir)
    if args.trace_file != '':
        state['params']['trace_file'] = args.trace_file
    else:
        state['params']['trace_file'] = os.path.join(state['params']['home_dir'], 'trace.log')
    if args.machine_config_file != '':
        state['params']['machine_config_file'] = args.machine_config_file
    else:
        state['params']['machine_config_file'] = os.path.join(state['params']['home_dir'], 'machine_config.log')
    state['params']['overwrite_logs'] = args.overwrite_logs
    state['params']['step'] = args.step


def init_state():
    initialize_report_writer(state)

    if not os.path.exists(state['params']['trace_file'])  \
        or not os.path.isfile(state['params']['trace_file']):
        raise Exception('Trace file incorrect')
    if not os.path.exists(state['params']['machine_config_file']) \
        or not os.path.isfile(state['params']['machine_config_file']):
        raise Exception('Machine configuration file file incorrect')

def main():
    args = parser.parse_args()
    store_params(args)
    init_state()

    create_report(state['params']['step'], state['params']['trace_file'], state['params']['machine_config_file'])


if __name__ == '__main__':
    main()
