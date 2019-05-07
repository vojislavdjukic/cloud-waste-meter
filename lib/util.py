from __future__ import print_function
import subprocess


def cmd(command):
    return subprocess.check_output(command, shell=True).decode('utf-8')
