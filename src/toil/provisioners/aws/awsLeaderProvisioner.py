#!/usr/bin/env python
# Copyright (C) 2015 UCSC Computational Genomics Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse

from boto.exception import EC2ResponseError

try:
    import boto
except ImportError:
    raise RuntimeError("You must install toil with the AWS extra to run this script")

from boto.ec2.connection import EC2Connection
from boto.iam import IAMConnection
from toil.provisioners.aws import AWSUserData
coreOSAMI='ami-14589274'

# flag for instance types, region, key_name


def getLeaderProfileName():
    """
    """
    policy = """
    {
        "Statement":
        [{
            "Effect":"Allow",
            "Action":["s3:*", "ec2:*", "sdb:*"],
            "Resource":"*"
        }]
    }
    """

    iam = IAMConnection()
    roleName='toil-leader-role'
    profileName='toil-leader-profile'
    policyName="toil-leader-policy"
    # we want to create IAM role for leader since we have that ability now
    # full access to ec2, s3, iam, simpleDB  -  check in cgcloud
    try:
        #get existing profile
        pass
    except:
        instance_profile = iam.create_instance_profile(profileName)
        role = iam.create_role(roleName)
        iam.add_role_to_instance_profile(instance_profile_name=profileName,
                                         role_name=roleName)
        iam.put_role_policy(role_name=roleName, policy_name=policyName,
                            policy_document=policy)
    return profileName


def getSecurityGroupName():
    """

    :return:
    """
    name = 'toil-appliance-group'
    # security group create/get. standard + all ports open within the group
    ec2 = EC2Connection()
    try:
        web = ec2.create_security_group(name, 'Toil appliance security group')
        # open port 22 for ssh-ing
        web.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
        # the following authorizes all port access within the web security group
        web.authorize(ip_protocol='tcp', from_port=0, to_port=9000, src_group=web)
    except EC2ResponseError:
        web = ec2.get_all_security_groups(groupnames=[name])[0]
    return name


def launchInstance(type, keyName):
    """

    :param type:
    :return:
    """
    profileName=getLeaderProfileName()
    securityName=getSecurityGroupName()
    ec2 = EC2Connection()
    ec2.run_instances(image_id=coreOSAMI, security_groups=[securityName], instance_type=type,
                      instance_profile_name=profileName, key_name=keyName, user_data=AWSUserData
                      )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--type', dest='type',
                        help='Instance type to launch')
    parser.add_argument('--keyName', dest='keyName',
                        help='Name of the AWS key pair to include on the instance')

    args = parser.parse_args()

    launchInstance(type=args.type, keyName=args.keyName)

# almost same user data as workers- how do stay DRY here? String formatting? I think yes.

