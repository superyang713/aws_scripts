#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Webotron: Deploy websites with AWS.

Webotron automates the process of deploying static websites to AWS.
- configure AWS S3 buckets
    - Create them
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS with AWS Route 53
- Configure a Content Delivery Network and SSL with AWS
"""

import boto3

import os


key_name = 'test'
key_path = key_name + '.pem'

session = boto3.Session(profile_name='pythonAutomation')
ec2 = session.resource('ec2')

key = ec2.create_key_pair(KeyName=key_name)


# The private key is saved in the current dir.
with open(key_path, 'w') as key_file:
    key_file.write(key.key_material)

os.chmod(key_path, 0o400)

ami_name = 'amzn2-ami-hvm-2.0.20180810-x86_64-gp2'
filters = [{'Name': 'name', 'Values': [ami_name]}]
img = list(ec2.images.filter(Owners=['amazon'], Filters=filters))[0]

instances = ec2.create_instances(
    ImageId=img.id,
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName=key.key_name
)

inst = instances[0]

inst.wait_until_running()
inst.reload()
print(inst.public_dns_name)
sg = ec2.SecurityGroup(inst.security_groups[0]['GroupId'])
sg.authorize_ingress(
    IpPermissions=[{
        'FromPort': 22,
        'ToPort': 22,
        'IpProtocol': 'TCP',
        'IpRanges': [{
            'CidrIp': '18.74.5.146/32'
        }]
    }]
)
