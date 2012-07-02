#===============================================================================
# Copyright 2012 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
import time
#============= standard library imports ========================
#import os
from src.testing.remote_base_tests import RemoteBaseTests

#============= local library imports  ==========================


class RemoteLaserTests(RemoteBaseTests):
    '''
    
    '''

class RemoteCO2Tests(RemoteLaserTests):
    port = 1067

class RemoteDiodeTests(RemoteLaserTests):
    port = 1068

    def testAA_EnableLaser(self):
        self._testOK('Enable')
        time.sleep(0.5)

    def testSetLaserPower(self):
        self._testOK('SetLaserPower 10')

    def testAC_DisableLaser(self):
        time.sleep(1)
        self._testOK('Disable')


#============= EOF =============================================
