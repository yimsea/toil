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

from boto.exception import EC2ResponseError, BotoServerError

try:
    import boto
except ImportError:
    raise RuntimeError("You must install toil with the AWS extra to run this script")




def launchInstance(type, keyName):
    """

    :param type:
    :return:
    """


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--type', dest='type', required=True,
                        help='EC2 instance type to launch')
    parser.add_argument('--keyName', dest='keyName', required=True,
                        help='Name of the AWS key pair to include on the instance')

    args = parser.parse_args()

    launchInstance(type=args.type, keyName=args.keyName)
