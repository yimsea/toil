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

AWSUserData="""#cloud-config

coreos:
    units:
    - name: "volume-mounting.service"
      command: "start"
      content: |
        [Unit]
        Description=mounts ephemeral volumes & bind mounts toil directories
        Author=cketchum@ucsc.edu
        After=docker.service

        [Service]
        Restart=always
        ExecStart=/usr/bin/bash -c 'set -x; \
            ephemeral_count=0; \
            possible_drives="/dev/xvdb /dev/xvdc /dev/xvdd /dev/xvde"; \
            drives=""; \
            directories="toil mesos docker"; \
            if (("$ephemeral_count" == "0" )); then \
                echo no ephemeral drive; \
                for directory in $directories; do \
                    sudo mkdir -p /var/lib/$directory; \
                done; \
                exit 0; \
            fi'

    - name: "toil-worker.service"
      command: "start"
      content: |
        [Unit]
        Description=toil-worker container
        Author=cketchum@ucsc.edu
        After=docker.service

        [Service]
        Restart=always
        ExecStart=/usr/bin/docker run --net=host cket/toil-leader:3.3.0--512d560dbef36e2ce6d9e89e1faa921829579a75 --registry=in_memory

"""
