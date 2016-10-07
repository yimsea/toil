# Copyright (C) 2015-2016 Regents of the University of California
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

from __future__ import absolute_import
import os
from argparse import ArgumentParser
from toil.common import Toil
from toil.job import Job
from toil.test import ToilTest
from toil.jobGraph import JobGraph

class JobGraphTest(ToilTest):
    
    def setUp(self):
        super(JobGraphTest, self).setUp()
        self.jobStorePath = self._getTestJobStorePath()
        parser = ArgumentParser()
        Job.Runner.addToilOptions(parser)
        options = parser.parse_args(args=[self.jobStorePath])
        self.toil = Toil(options)
        self.assertEquals( self.toil, self.toil.__enter__() )

    def tearDown(self):
        self.toil.__exit__(None, None, None)
        self.toil._jobStore.destroy()
        self.assertFalse(os.path.exists(self.jobStorePath))
        super(JobGraphTest, self).tearDown()
    
    def testJob(self):       
        """
        Tests functions of a job.
        """ 
    
        command = "by your command"
        memory = 2^32
        disk = 2^32
        cores = 1
        preemptable = 1
        jobStoreID = 100
        remainingRetryCount = 5
        predecessorNumber = 0
        
        j = JobGraph(command, memory, cores, disk, preemptable, jobStoreID,
                     remainingRetryCount, predecessorNumber)
        
        #Check attributes
        #
        self.assertEquals(j.command, command)
        self.assertEquals(j.memory, memory)
        self.assertEquals(j.disk, disk)
        self.assertEquals(j.cores, cores)
        self.assertEquals(j.preemptable, preemptable)
        self.assertEquals(j.jobStoreID, jobStoreID)
        self.assertEquals(j.remainingRetryCount, remainingRetryCount)
        self.assertEquals(j.predecessorNumber, predecessorNumber)
        self.assertEquals(j.stack, [])
        self.assertEquals(j.predecessorsFinished, set())
        self.assertEquals(j.logJobStoreFileID, None)
        
        #Check equals function
        j2 = JobGraph(command, memory, cores, disk, preemptable, jobStoreID,
                      remainingRetryCount, predecessorNumber)
        self.assertEquals(j, j2)
        #Change an attribute and check not equal
        j.predecessorsFinished = {"1", "2"}
        self.assertNotEquals(j, j2)
        
        ###TODO test other functionality
