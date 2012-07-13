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
#need to build the global paths structure
from src.paths import paths
paths.build('_test')

#from laser_tests import DiodeTests, CO2Tests
#from extraction_line_tests import ExtractionLineTests
#from remote_extraction_line_tests import RemoteExtractionLineTests
#from remote_laser_tests import RemoteDiodeTests, RemoteCO2Tests




#from device_scan_db_tests import DeviceScanDBTests
from isotope_db_tests import IsotopeDBTests

#============= EOF =============================================
