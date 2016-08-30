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
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
from boto.exception import BotoServerError, EC2ResponseError
from toil.provisioners.abstractProvisioner import AbstractProvisioner, Shape
from toil.provisioners.aws import AWSUserData
from cgcloud.lib.context import Context
from boto.utils import get_instance_metadata


coreOSAMI = 'ami-14589274'
ec2_full_policy = dict( Version="2012-10-17", Statement=[
    dict( Effect="Allow", Resource="*", Action="ec2:*" ) ] )

s3_full_policy = dict( Version="2012-10-17", Statement=[
    dict( Effect="Allow", Resource="*", Action="s3:*" ) ] )

sdb_full_policy = dict( Version="2012-10-17", Statement=[
    dict( Effect="Allow", Resource="*", Action="sdb:*" ) ] )


class AWSProvisioner(AbstractProvisioner):

    def __init__(self):
        # Do we have to delete instance profiles? What about security group?
        self.ctx = Context(availability_zone='us-west-2a', namespace='/')
        self.securityGroupName = get_instance_metadata()['security-groups'][0]


    def setNodeCount(self, numNodes, preemptable=False, force=False):
        # methods:
        # determine number of ephemeral drives via cgcloud-lib
        bdt = BlockDeviceType()
        # bdd = {'/dev/xvdb'} etc....
        bdm = BlockDeviceMapping()
        # get all nodes in cluster
        instances = self._getAllNodesInCluster()
        # get security group
        SGName = self.getSecurityGroupName(self.ctx)
        intancesToLaunch = len(instances) - numNodes
        for instance in intancesToLaunch:
            id = 'xxxxxxx' # uuid?
            arn = self.getProfileARN(self.ctx, instanceID=id)
            #launch

        pass

    def getNodeShape(self, preemptable=False):
        pass

    def _getAllNodesInCluster(self):
        return self.ctx.ec2.get_only_instances(filters={
            'tag:leader_instance_id': self._instanceId, # instead do AMI ID? > Our launch time?
            'instance-state-name': 'running'})

    @staticmethod
    def launchLeaderInstance(instanceType, keyName):
        nameSpace = '/'+keyName.split('@')[0]+'/'
        ctx = Context(availability_zone='us-west-2a', namespace=nameSpace)
        profileARN = AWSProvisioner.getProfileARN(ctx, instanceID='leader')
        securityName = AWSProvisioner.getSecurityGroupName(ctx)

        ctx.ec2.run_instances(image_id=coreOSAMI, security_groups=[securityName], instance_type=instanceType,
                              instance_profile_arn=profileARN, key_name=keyName, user_data=AWSUserData)

    @staticmethod
    def getSecurityGroupName(ctx):
        name = 'toil-appliance-group' # fixme: should be uuid
        # security group create/get. standard + all ports open within the group
        try:
            web = ctx.ec2.create_security_group(name, 'Toil appliance security group')
            # open port 22 for ssh-ing
            web.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
            # the following authorizes all port access within the web security group
            web.authorize(ip_protocol='tcp', from_port=0, to_port=9000, src_group=web)
        except EC2ResponseError:
            web = ctx.ec2.get_all_security_groups(groupnames=[name])[0]
        return name

    @staticmethod
    def getProfileARN(ctx, instanceID):
        roleName='toil-leader-role'
        awsInstanceProfileName = roleName+instanceID
        policy = {}
        policy.update( dict(
            toil_iam_pass_role=dict(
                Version="2012-10-17",
                Statement=[
                    dict( Effect="Allow", Resource="*", Action="iam:PassRole" ) ] ),
            ec2_full=ec2_full_policy,
            s3_full=s3_full_policy,
            sbd_full=sdb_full_policy,
            ec2_toil_box=dict( Version="2012-10-17", Statement=[
            dict( Effect="Allow", Resource="*", Action="ec2:CreateTags" ),
            dict( Effect="Allow", Resource="*", Action="ec2:CreateVolume" ),
            dict( Effect="Allow", Resource="*", Action="ec2:AttachVolume" ) ] ) ) )

        profileName = ctx.setup_iam_ec2_role(role_name=roleName, policies=policy)
        try:
            profile = ctx.iam.get_instance_profile(awsInstanceProfileName)
        except BotoServerError as e:
            if e.status == 404:
                profile = ctx.iam.create_instance_profile( awsInstanceProfileName )
                profile = profile.create_instance_profile_response.create_instance_profile_result
            else:
                raise
        else:
            profile = profile.get_instance_profile_response.get_instance_profile_result
        profile = profile.instance_profile
        profile_arn = profile.arn

        if len( profile.roles ) > 1:
                raise RuntimeError( 'Did not expect profile to contain more than one role' )
        elif len( profile.roles ) == 1:
            # this should be profile.roles[0].role_name
            if profile.roles.member.role_name == roleName:
                return profile_arn
            else:
                ctx.iam.remove_role_from_instance_profile( awsInstanceProfileName,
                                                                profile.roles.member.role_name )
        ctx.iam.add_role_to_instance_profile( awsInstanceProfileName, roleName )
        return profile_arn
