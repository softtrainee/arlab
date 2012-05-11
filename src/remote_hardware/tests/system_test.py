#===============================================================================
# Copyright 2011 Jake Ross
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
#import unittest
#============= local library imports  ==========================
#from src.remote_hardware.remote_hardware_manager import RemoteHardwareManager
from src.remote_hardware.protocols.system_protocol import SystemProtocol
from src.remote_hardware.tests.base_test import baseTest
from src.remote_hardware.errors import InvalidCommandErrorCode, \
    NoResponseErrorCode, InvalidArgumentsErrorCode


class SystemTest(baseTest):
    protocol = SystemProtocol

    def testTest(self):
        data = 'data'
        v = data
        self._test('test', data, v)

    def testOpen(self):
        data = ['Open A', 'Opend A']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite('System', data, vs)

    def testClose(self):
        data = ['Close A', ('close A', 'Close A,B')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite('System', data, vs)

    def testGetValveState(self):
        data = ['GetValveState A', 'GetValveStated A']
        vs = ['True', InvalidCommandErrorCode]
        self._test_suite('System', data, vs)

    def testGetManualState(self):
        data = ['GetManualState A', 'GetManualStatde A']
        vs = ['False', InvalidCommandErrorCode]
        self._test_suite('System', data, vs)

    def testRead(self):
        data = ['Read bakeout1', 'Mead bakeout1']
        vs = ['0.1', InvalidCommandErrorCode]
        self._test_suite('System', data, vs)

        data = 'Read "diode tr"'
        v = '0.1'
        self._test('System', data, v)

    def testSet(self):
        data = ['Set "bakeout1" 10', 'Pet "bakeout1" 10']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite('System', data, vs)

    def testGetValveStates(self):
        data = ['GetValveStates', 'getValveStates']
        vs = ['True,True,False', InvalidCommandErrorCode]
        self._test_suite('System', data, vs)
#        
#    def testRemoteLaunch(self):
#        data = 'RemoteLaunch'
#        v = 'OK'
#        self._test('System', data, v)
#    
#    def testPychronReady(self):
#        data = 'PychronReady'
#        v = 'OK'
#        self._test('System', data, v)

    def testStartMultRuns(self):
        data = ['StartMultRuns 1254']
        vs = ['2 : manager unavaliable: TwitterManager']
        self._test_suite('System', data, vs)

    def testCompleteMultRuns(self):
        data = ['CompleteMultRuns 1254']
        vs = ['2 : manager unavaliable: TwitterManager']
        self._test_suite('System', data, vs)


#============= EOF ====================================
