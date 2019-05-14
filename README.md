# Cloud Waste Meter

Cloud waste meter measures utilization of cloud virtual machines and calculates what is the cost of unused resources.

### Monitor system utilization

To monitor the utilization of a particular virtual machine over time, run: 

`python meter.py`

This script creates two files within `~/.wastemeter`:

+ __trace.log__ contains resource utilization at a particular point in time
+ __machine_config.log__ contains resource configuration of the virtual machine at different points in time. For environments that do not change their resource configuration over time (e.g. fixed number of CPU cores, memory...), this file contains only one configuration.

`meter.py` measures utilization of 3 main resources in the machine: CPU, Memory and Network. Every `-f` seconds (script parameter), the script calculates the utilization from the following files:

+ CPU utilization using `/proc/stat` file
+ Memory utilization using `/proc/meminfo` file
+ Network utilization using `/proc/net/dev` file

By default, the script parses those files every second and saves the result in `trace.log`.

### Calculate the waste

(under construction)