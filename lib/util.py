from __future__ import print_function

import subprocess
import os
import json
import requests

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.5f')

aws_data_path = out = os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir,'data','aws_data.json')

def cmd(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    stdout_value = p.communicate()[0].decode('utf-8')
    return stdout_value   # the output
    #return subprocess.check_output(command, shell=True).decode('utf-8')

def prepare_aws_pricing():
    r = requests.get('https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json')
    r = r.json()
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
        "China (Beijing)": "cn-north-1",
        "China (Ningxia)": "cn-northwest-1",
        "EU (Frankfurt)": "eu-central-1",
        "EU (Ireland)": "eu-west-1",
        "EU (London)": "eu-west-2",
        "EU (Paris)": "eu-west-3",
        "EU (Stockholm)": "eu-north-1",
        "South America (Sao Paulo)": "sa-east-1",
        "AWS GovCloud (US-East)": "us-gov-east-1",
        "AWS GovCloud (US)": "us-gov-west-1"    
    }

    print('Downlaoad finished')
    result = {}
    for i in region_mapping:
        result[region_mapping[i]] = {}

    for product in r['products']:
        attributes = r['products'][product]['attributes']
        if 'instanceType' not in attributes or attributes['location'] not in region_mapping \
        or not attributes['operatingSystem'] == 'Linux':
            continue
        region = region_mapping[attributes['location']]
        instance_type = attributes['instanceType']
        memory = attributes['memory']
        if ' GiB' in memory:
            memory = memory.replace(' GiB', '')
        if ',' in memory:
            memory = memory.replace(',', '')
        if memory == 'NA':
            continue
        memory = float(memory)
        cpu = float(attributes['vcpu'])
        
        network = attributes['networkPerformance'].replace(' Gigabit', '')
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

        if product not in r['terms']['OnDemand']:
            continue
        prices = r['terms']['OnDemand'][product].values()


        pp = []
        for price in prices:
            t = price['priceDimensions'].values()
            for x in t:
                pp.append(float(x['pricePerUnit']['USD']))
        
        cost = max(pp)
        
        if instance_type == "t3.nano" and region == 'ap-east-1':
            print(region, pp)
            print(attributes)

        if instance_type in result[region]:
            result[region][instance_type]['cost'] = max(result[region][instance_type]['cost'], cost)
        else:
            result[region][instance_type] = {
                'cpu': cpu,
                'memory': memory,
                'network': network,
                'cost': cost   
            }

    print('Conversion finished')
    
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
    

