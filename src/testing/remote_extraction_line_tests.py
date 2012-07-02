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
#============= standard library imports ========================

#============= local library imports  ==========================
from src.testing.remote_base_tests import RemoteBaseTests


class RemoteExtractionLineTests(RemoteBaseTests):
    port = 1061

#===============================================================================
# A Group
#===============================================================================
    def testA_PychronReady(self):
        c = self.client
        r = c.ask('PychronReady', verbose=False)
        self.assertEqual(r, 'OK')

#===============================================================================
# B Group
#===============================================================================
    def testBA_OpenValve(self):
        self._testOK('Open B')
        self._testOK('Open B')

    def testBB_CloseValve(self):
        self._testOK('Close B')
        self._testOK('Close B')


#============= EOF =============================================
