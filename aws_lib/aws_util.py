#!/usr/bin/env python

""" 
AWS Utilities

"""

__author__      = "Rahul R Nair"
__date__        = "2024/09/13"
__deprecated__  = False
__email__       = "rahul7manu@gmail.com"
__maintainer__  = "Rahul R Nair"
__status__      = "Development"
__version__     = "0.0.1"

import os
import sys
import time
import shutil

import boto3
import argparse
import zipfile

import cv2
import open3d as o3d
import pandas as pd

import yaml
from yaml.loader import SafeLoader
# from aws-doc-sdk-examples/python/
from example_code.secretsmanager import get_secret_value as gsv
from example_code.ec2 import instance
from example_code.ec2.hello import hello_ec2
from example_code.s3.s3_basics import hello
from test_tools import ec2_stubber

class AwsUtil():
    # initialize
    def __init__(self):
        start_time = time.time()
        print('ENTRY: ',self.__class__.__name__,'::',sys._getframe().f_code.co_name,'() -> started!')

        ### CONFIG
        # Setting the relative path for data (image and input config) directory
        self.config_dir = './config/'

        try:
            if not os.path.isdir(self.config_dir):
                os.mkdir(self.config_dir)
        except OSError as error:
            print(error)
        
        config_file_name = self.config_dir + 'aws_s3_config.yaml'

        # Open the file and load the file
        with open(config_file_name) as f:
            self.config_data = yaml.load(f, Loader=SafeLoader)

        self.bucket_name    = self.config_data['bucket_name']
        self.aws_access_key = self.config_data['aws_access_key']
        self.aws_secret_key = self.config_data['aws_secret_key']
        self.region         = self.config_data['region']

        self.s3_client = boto3.client('s3', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region)
        self.ec2_client = boto3.client('ec2', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region)
        self.sm_client = boto3.client('secretsmanager', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region)
        
        self.s3_resource = boto3.resource('s3', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region)
        self.ec2_resource = boto3.resource('ec2', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region)
        self.cloudwatch = boto3.resource('cloudwatch', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region)

        # log the current class, function name and time taken to execute
        print('EXIT: ',self.__class__.__name__,'::',sys._getframe().f_code.co_name,'() -> executed in', round(time.time() - start_time, 6), 'seconds!')

    def hello_ec2(self):
        ec2_resource=self.ec2_resource
        """
        Use the AWS SDK for Python (Boto3) to create an Amazon Elastic Compute Cloud
        (Amazon EC2) resource and list the security groups in your account.
        This example uses the default settings specified in your shared credentials
        and config files.

        :param ec2_resource: A Boto3 EC2 ServiceResource object. This object is a high-level
                            resource that wraps the low-level EC2 service API.
        """
        print("Hello, Amazon EC2! Let's list up to 10 of your security groups:")
        for sg in ec2_resource.security_groups.limit(10):
            print(f"\t{sg.id}: {sg.group_name}")
        
    def hello_s3(self):
        """
        Use the AWS SDK for Python (Boto3) to create an Amazon Simple Storage Service
        (Amazon S3) resource and list the buckets in your account.
        This example uses the default settings specified in your shared credentials
        and config files.
        """   
        s3_resource = self.s3_resource
        print("Hello, Amazon S3! Let's list your buckets:")
        for bucket in s3_resource.buckets.all():
            print(f"\t{bucket.name}")
        
        bucket = s3_resource.Bucket(self.bucket_name)
        print(bucket)
        print(bucket.objects)
        print(type(bucket.objects.all()))
        # for obj in bucket.objects.all():
        #     print(obj.key)

if __name__ == "__main__":
    
    aws = AwsUtil()

    ## SECRET MANAGER
    # gsw = gsv.GetSecretWrapper(aws.sm_client)
    # print(gsw.get_secret('mySecret'))

    ## HELLO EC2 and S3
    hello_ec2.hello_ec2(aws.ec2_resource)
    hello.hello_s3(aws.s3_resource)

    ## INSTANCE
    ec2_stub = ec2_stubber.Ec2Stubber(aws.ec2_client)
    print(aws.ec2_resource.instances)
    for ins in aws.ec2_resource.instances.all():
        # print(ins)
        ins_wrpr = instance.InstanceWrapper(aws.ec2_resource, ins)
        ins_wrpr.display()
        print(ins.id)
        ins_wrpr.get_instance_types('micro')
        if ins.id != '':
            # if ins.state['Name'] == 'stopped':
            #     ins.start()
            #     break
            # if ins.state['Name'] == 'running':
            #     ins.stop()
            #     break
            print('instance-3:              ', ins.id)
            print('ins.cpu_options:         ', ins.cpu_options)
            print('ins.client_token:        ', ins.client_token)
            print('ins.tags:                ', ins.tags)
            print('ins.public_ip_address:   ', ins.public_ip_address)
            print('ins.private_ip_address:  ', ins.private_ip_address)

            print('ins.tag_name:            ', ins.tags[0]['Value'])
            # ins.create_tags(Tags=[{'Key': 'Name','Value': 'RAHUL'},])
        
    # print(ec2_stub.stub_describe_instances(aws.ec2_resource.instances.all()))
