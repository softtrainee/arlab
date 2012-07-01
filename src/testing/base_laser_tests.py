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
import os
from unittest import TestCase

#============= local library imports  ==========================
from src.lasers.power.power_calibration_manager import PowerCalibrationObject


class BaseLaserTests(TestCase):
    '''
         tests are run in alphabetically order 
         
    '''

#===============================================================================
# A Group
#===============================================================================
    def testAB_GetLaserManager(self):
        self.assertNotEqual(self._laser, None)

    def testAC_GetStageManager(self):
        self.assertNotEqual(self._stage, None)

    def testAD_GetStageController(self):
        self.assertNotEqual(self._stage_controller, None)


#===============================================================================
# B Group
#===============================================================================
    def testBA_PositioningErrorPreMove(self):
        sm = self._stage
        sm.video.open(user='testing')
        args = sm._autocenter()
        if args:
            p1 = -0.095402853829520087, 0.14764042643757608
            self.assertPositionEqual(p1, args[0])

    def testBB_MoveXY_Noncalibrated(self):
        sm = self._stage
        sc = self._stage_controller
        x = 5.4
        y = 4.3
        sm.linear_move(x, y, block=True, use_calibration=False)
        self.assertEqual(x, sc.x)
        self.assertEqual(y, sc.y)

    def testBC_PositioningErrorPostMove(self):
        sm = self._stage
        sm.video.open(user='testing')
        args = sm._autocenter()
        if args:
            p1 = 5.3045971461704795, 4.4476404264375757
            self.assertPositionEqual(p1, args[0])

    def testBD_MoveToHole(self):
        sm = self._stage
        sc = self._stage_controller
        sm._move_to_hole('3')

        p1 = -12.035103242609356, 8.5679304729336643
        self.assertPositionEqual(p1, map(sc.get_current_position, ('x', 'y')))

    def testBE_ClearCorrections(self):
        sm = self._stage
        p = sm._stage_map.clear_correction_file()
        self.assertFalse(os.path.isfile(p))


#===============================================================================
# C Group
#===============================================================================
    def testCA_DumpPowerCalibration(self):
        man = self._laser
        man.dump_power_calibration(coefficients=self._power_calibration_coeffs,
                                   calibration_path=self._power_calibration_path)
        self.assertTrue(os.path.isfile(self._power_calibration_path), True)

    def testCB_LoadPowerCalibration(self):
        man = self._laser
        pc = man.load_power_calibration(calibration_path=self._power_calibration_path)
        self.assertIsInstance(pc, PowerCalibrationObject)
        self.assertListEqual(pc.coefficients, self._power_calibration_coeffs)

    def testCD_LoadPowerCalibrationCorrupted(self):
        man = self._laser
        p = '{}_corrupt'.format(self._power_calibration_path)
        pc = man.load_power_calibration(calibration_path=p)
        self.assertIsInstance(pc, PowerCalibrationObject)
        self.assertListEqual(pc.coefficients, [1, 1])

#===============================================================================
# D Group
#===============================================================================
    def testDA_EnableLaser(self):
        man = self._laser
        r = man.enable_laser()
        self.assertTrue(r)
        self.assertTrue(man.monitor.is_monitoring())

    def testDB_SetCalibratedPower(self):
        man = self._laser
        man.set_laser_power(10, use_calibration=self._power_calibration_path)
        self.assertEqual(man._requested_power, 10)
        self.assertEqual(man._calibrated_power, self._calibrated_power)

    def testDC_SetPercentPower(self):
        man = self._laser
        n = 10
        man.set_laser_power(n, use_calibration=False)
        self.assertEqual(man._requested_power, n)
        self.assertEqual(man._calibrated_power, n)

    def testDD_DisableLaser(self):
        man = self._laser
        r = man.disable_laser()
        self.assertTrue(r)
        self.assertFalse(man.monitor.is_monitoring())

#===============================================================================
# E Group
#===============================================================================
    def testEA_DumpStageCalibration(self):
        pass
    def testEB_LoadStageCalibration(self):
        pass
#===============================================================================
# TestCase protocol
#===============================================================================
    def assertPositionEqual(self, p1, p2):
        self.assertAlmostEqual(p1[0], p2[0])
        self.assertAlmostEqual(p1[1], p2[1])




#============= EOF =============================================
