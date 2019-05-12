from __future__ import print_function
import subprocess
import os


def cmd(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    stdout_value = p.communicate()[0].decode('utf-8')
    return stdout_value   # the output
    #return subprocess.check_output(command, shell=True).decode('utf-8')
