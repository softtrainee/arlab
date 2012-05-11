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
from src.database.adapters.database_adapter import DatabaseAdapter
from src.database.selectors.device_scan_selector import DeviceScanSelector
from src.database.orms.device_scan_orm import ScanTable, DeviceTable, PathTable
from src.helpers.paths import device_scan_db

class DeviceScanAdapter(DatabaseAdapter):
    test_func = None
    selector_klass = DeviceScanSelector
#==============================================================================
#    getters
#==============================================================================

    def get_scans(self, **kw):
        return self._get_items(ScanTable, globals(), **kw)

#=============================================================================
#   adder
#=============================================================================
    def add_scan(self, device, commit=False, **kw):
#        b = PowerMapTable(**kw)
        b = self._add_timestamped_item(ScanTable, commit)

        if isinstance(device, str):
            device = self.get_device()

        device.scans.append(b)
        return b
#
    def add_device(self, name, unique=True, commit=False, **kw):
        kw['name'] = name

        c = DeviceTable(**kw)
        if unique:
            sess = self.get_session()
            q = sess.query(DeviceTable).filter_by(name=name)
            add_item = not bool(q.count())
            if not add_item:
                c = q.one()
        else:
            add_item = True

        if add_item:
            self._add_item(c, commit)

        return c
#
    def add_path(self, scan, path, commit=False, **kw):
        kw = self._get_path_keywords(path, kw)
        p = PathTable(**kw)
        scan.path = p
        if commit:
            self.commit()
        return p

if __name__ == '__main__':
    db = DeviceScanAdapter(dbname=device_scan_db,
                            kind='sqlite')
    db.connect()

    dbs = DeviceScanSelector(_db=db)
    dbs._execute_()
    dbs.configure_traits()
#    print db.get_bakeouts(join_table='ControllerTable',
#                    filter_str='ControllerTable.script="---"'
#                    )


#============= EOF =============================================
