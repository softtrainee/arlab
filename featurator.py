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
'''
test features of pychron using unittest



'''

#import unittest
#===============================================================================
# ImportTest
#===============================================================================
#class ImportTest(unittest.TestCase):
#
#    def setUp(self):
#        pass
#    def testELM(self):
#        from src.managers.extraction_line_manager import ExtractionLineManager
#        e = ExtractionLineManager()
#        self.assertEqual(e.__class__, ExtractionLineManager)
#
#    def testFusionsCO2(self):
#        from src.managers.laser_managers.fusions_co2_manager import FusionsCO2Manager
#        e = FusionsCO2Manager()
#        self.assertEqual(e.__class__, FusionsCO2Manager)
#
#    def testFusionsDiode(self):
#        from src.managers.laser_managers.fusions_diode_manager import FusionsDiodeManager
#        e = FusionsDiodeManager()
#        self.assertEqual(e.__class__, FusionsDiodeManager)
#
#    def testStageManager(self):
#        from src.managers.stage_managers.stage_manager import StageManager
#        e = StageManager()
#        self.assertEqual(e.__class__, StageManager)
#
#    def testVideoStageManager(self):
#        from src.managers.stage_managers.video_stage_manager import VideoStageManager
#        e = VideoStageManager()
#        self.assertEqual(e.__class__, VideoStageManager)

#===============================================================================
# RemoteHardwareTest
#===============================================================================
from src.remote_hardware.tests.laser_test import LaserTest
from src.remote_hardware.tests.system_test import SystemTest



