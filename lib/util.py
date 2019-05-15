from __future__ import print_function

import subprocess
import os
import json
import requests

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.5f')

aws_data_path = out = os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir,'data','aws_data.json')
aws_url = 'https://a0.p.awsstatic.com/pricing/1.0/ec2/region/%s/ondemand/linux/index.json'


def cmd(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    stdout_value = p.communicate()[0].decode('utf-8')
    return stdout_value   # the output
    #return subprocess.check_output(command, shell=True).decode('utf-8')

def prepare_aws_pricing():
    region_mapping = {
        "US East (Ohio)": "us-east-2",
        "US East (N. Virginia)": "us-east-1",
        "US West (N. California)": "us-west-1",
        "US West (Oregon)": "us-west-2",
        "Asia Pacific (Hong Kong)": "ap-east-1",
        "Asia Pacific (Mumbai)": "ap-south-1",
        "Asia Pacific (Seoul)": "ap-northeast-2",
        "Asia Pacific (Singapore)": "ap-southeast-1",
        "Asia Pacific (Sydney)": "ap-southeast-2",
        "Asia Pacific (Tokyo)": "ap-northeast-1",
        "Canada (Central)": "ca-central-1",
        #"China (Beijing)": "cn-north-1",
        #"China (Ningxia)": "cn-northwest-1",
        "EU (Frankfurt)": "eu-central-1",
        "EU (Ireland)": "eu-west-1",
        "EU (London)": "eu-west-2",
        "EU (Paris)": "eu-west-3",
        "EU (Stockholm)": "eu-north-1",
        "South America (Sao Paulo)": "sa-east-1",
        "AWS GovCloud (US-East)": "us-gov-east-1",
        "AWS GovCloud (US)": "us-gov-west-1"    
    }

    result = {}
    for region in region_mapping.values():
        print("Downloading the region: %s"%region)
        r = requests.get(aws_url%region)
        r = r.json()
        result[region] = {}

        for instance in r['prices']:
            attributes = instance['attributes']
            instance_type = attributes['aws:ec2:instanceType']
            memory = attributes['aws:ec2:memory']
            if ' GiB' in memory:
                memory = memory.replace(' GiB', '')
            if ',' in memory:
                memory = memory.replace(',', '')
            if memory == 'NA':
                continue
            memory = float(memory)
            cpu = float(attributes['aws:ec2:vcpu'])
            
            network = attributes['aws:ec2:networkPerformance'].replace(' Gigabit', '')
            if 'Low' in network:
                network = '1'
            elif 'Moderate' in network:
                network = '2'
            elif 'High' in network:
                network = '3'
            if 'Up to ' in network:
                network = network.replace('Up to ', '')
            if network == 'NA':
                continue
            network = float(network)
            cost = float(instance['price']['USD'])
            result[region][instance_type] = {
                'cpu': cpu,
                'memory': memory,
                'network': network,
                'cost': cost   
            }
    
    with open(aws_data_path, 'w') as outfile:  
        json.dump(result, outfile, indent=4, sort_keys=True)

    return result

def load_aws_pricing():
    if os.path.exists(aws_data_path):
        with open(aws_data_path) as f:
            data = json.load(f)
            return data
    else:
        return prepare_aws_pricing()
    

