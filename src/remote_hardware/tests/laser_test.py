'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================

#============= standard library imports ========================
#============= local library imports  ==========================
from src.remote_hardware.protocols.laser_protocol import LaserProtocol
from src.remote_hardware.tests.base_test import baseTest
from src.remote_hardware.errors import InvalidCommandErrorCode, \
    InvalidArgumentsErrorCode

request_types = ['Diode']  # , 'CO2', 'Synrad']


class LaserTest(baseTest):
    protocol = LaserProtocol

    def testGetDriveMoving(self):
        data = ['GetDriveMoving', 'getDriveMoving']
        vs = ['True', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testStopDrive(self):
        data = ['StopDrive', 'stopDrive']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testGoToHole(self):
        data = ['GoToHole 1', ('GoTohole 1', 'GoToHole', 'GoToHole 1a')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testAbortJog(self):
        data = ['AbortJog', 'abortJog']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetSampleHolder(self):
        data = ['SetSampleHolder Ba', ('setsampleHolder', 'SetSampleHolder')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testGetSampleHolder(self):
        data = ['GetSampleHolder', 'getSampleHolder']
        vs = ['221-hole', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testGetPosition(self):
        data = ['GetPosition', 'getPosition']
        vs = ['0.00,0.00,1.00', InvalidCommandErrorCode]

        self._test_suite(request_types, data, vs)

    def testSetXY(self):
        data = ['SetXY 1,1', ('setXY 1,1', 'SetXY')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testSetX(self):
        data = ['SetX 3', ('setX 3', 'SetX', 'SetX 3a')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testSetY(self):
        data = ['SetY 3', ('setY 3', 'SetY', 'SetY 3A')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testSetZ(self):
        data = ['SetZ 3', ('setZ 3', 'SetZ', 'SetZ 3A')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testGetXMoving(self):
        data = ['GetXMoving', 'getXMoving']
        vs = ['True', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testGetYMoving(self):
        data = ['GetYMoving', 'getYMoving']
        vs = ['True', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testGetZMoving(self):
        data = ['GetZMoving', 'getZMoving']
        vs = ['True', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetDriveHome(self):
        data = ['SetDriveHome', 'setDriveHome']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetHomeX(self):
        data = ['SetHomeX', 'setHomeX']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetHomeY(self):
        data = ['SetHomeY', 'setHomeY']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetHomeZ(self):
        data = ['SetHomeZ', 'setHomeZ']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testGetJogProcedures(self):
        data = ['GetJogProcedures', 'getJogProcedures']
        vs = ['PatternA,PatternB', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testJogName(self):
        data = ['JogName A', ('jogName', 'JogName')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testSetBeamDiameter(self):
        data = ['SetBeamDiameter 1', ('setBeamDiameter', 'SetBeamDiameter', 'SetBeamDiameter 3a')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testGetBeamDiameter(self):
        data = ['GetBeamDiameter', 'getBeamDiameter']
        vs = ['1.5', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetZoom(self):
        data = ['SetZoom 1', ('setZoom 1', 'SetZoom', 'SetZoom 3A')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

    def testGetZoom(self):
        data = ['GetZoom', 'getZoom']
        vs = ['30', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testEnable(self):
        data = ['Enable', 'enable']
        v = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, v)

    def testDisable(self):
        data = ['Disable', 'disable']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testReadLaserPower(self):
        data = ['ReadLaserPower', 'readLaserPower']
        vs = ['14.0', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testGetLaserStatus(self):
        data = ['GetLaserStatus', 'getLaserStatus']
        vs = ['OK', InvalidCommandErrorCode]
        self._test_suite(request_types, data, vs)

    def testSetLaserPower(self):
        data = ['SetLaserPower 10', ('setLaserPower 10', 'SetLaserPower', 'SetLaserPower 3d')]
        vs = ['OK', (InvalidCommandErrorCode, InvalidArgumentsErrorCode, InvalidArgumentsErrorCode)]
        self._test_suite(request_types, data, vs)

#============= EOF ====================================
