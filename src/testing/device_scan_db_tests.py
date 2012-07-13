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
#from traits.api import HasTraits
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from os import path
#============= local library imports  ==========================
from database_tests import BaseDatabaseTests
from src.database.adapters.device_scan_adapter import DeviceScanAdapter
from src.paths import paths


class DeviceScanDBTests(BaseDatabaseTests):


    @classmethod
    def _db_factory(self):
        db = DeviceScanAdapter(kind='sqlite',
                             dbname=path.join(paths.test_dir, 'scans_test.sqlite')
                             )
        return db



#===============================================================================
# tests
#===============================================================================

    def testBA_AddDevice(self):
        db = self._db
        d = db.add_device('TestDevice', commit=True)

        from src.database.orms.device_scan_orm import DeviceTable
        self.assertIsInstance(d, DeviceTable)

    def testBB_AddScan(self):
        db = self._db
        s = db.add_scan('TestDevice', commit=True)
        from src.database.orms.device_scan_orm import ScanTable
        self.assertIsInstance(s, ScanTable)

    def testCA_GetDevices(self):
        db = self._db
        d = db.get_devices()
        self.assertEqual(len(d), 1)

    def testCB_GetScans(self):
        db = self._db
        s = db.get_scans()
        self.assertEqual(len(s), 1)

    def testDA_DeleteDevice(self):
        self._delete('delete_device', 'TestDevice', 'get_devices')

    def testDB_DeleteScan(self):
        self._delete('delete_scan', 1, 'get_scans')


#============= EOF =============================================
