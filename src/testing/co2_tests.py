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

#============= local library imports  ==========================
from src.paths import paths
from src.testing.base_laser_tests import BaseLaserTests


class CO2Tests(BaseLaserTests):
    def setUp(self):
        from src.envisage.run import app
        self.app = app

        dp = 'src.lasers.laser_managers.fusions_co2_manager.FusionsCO2Manager'
        self._laser = app.get_service(dp)
        self._stage = self._laser.stage_manager
        self._stage_controller = self._stage.stage_controller

        self._power_calibration_path = os.path.join(paths.test_dir, 'co2_test_power_calibration')
        self._power_calibration_coeffs = [2, 5]
        self._calibrated_power = 2.5
#============= EOF =============================================
