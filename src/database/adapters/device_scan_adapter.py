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
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = "qt4"
#============= enthought library imports =======================
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.adapters.database_adapter import PathDatabaseAdapter
from src.database.selectors.device_scan_selector import DeviceScanSelector
from src.database.orms.device_scan_orm import ScanTable, DeviceTable, \
    ScanPathTable
from src.database.adapters.functions import get_one, delete_one

class DeviceScanAdapter(PathDatabaseAdapter):
    test_func = None
    selector_klass = DeviceScanSelector
    path_table = ScanPathTable
#==============================================================================
#    getters
#==============================================================================


    @get_one
    def get_device(self, name):
        return DeviceTable

    @get_one
    def get_scan(self, sid):
        return (DeviceTable, 'id')

    def get_devices(self, **kw):
        return self._get_items(DeviceTable, globals(), **kw)

    def get_scans(self, **kw):
        return self._get_items(ScanTable, globals(), **kw)
#=============================================================================
#   adder
#=============================================================================
    def add_scan(self, device, commit=False, **kw):
#        b = PowerMapTable(**kw)
        b = self._add_timestamped_item(ScanTable, commit, **kw)

        if isinstance(device, str):
            device = self.get_device(device)

        device.scans.append(b)
        if commit:
            self.commit()

        return b
#
    def add_device(self, name, unique=True, commit=False, **kw):

        kw['name'] = name
        c = DeviceTable(**kw)
        if unique:
            sess = self.get_session()
            q = sess.query(DeviceTable).filter(DeviceTable.name == name)
            add_item = not bool(q.count())
            if not add_item:
                c = q.one()
        else:
            add_item = True

        if add_item:
            self._add_item(c, commit)

        return c


    @delete_one
    def delete_device(self, name):
#        sess = self.get_session()
#        q = sess.query(DeviceTable).filter(DeviceTable.name == name)
#        try:
#            dev = q.one()
#
#            sess.delete(dev)
#            if commit:
#                sess.commit()
#
#        except Exception, e:
#            print e
        return DeviceTable

    @delete_one
    def delete_scan(self, sid):
        return ScanTable, 'id'


if __name__ == '__main__':

    from src.helpers.logger_setup import logging_setup
    logging_setup('dvs')

    from src.paths import paths
    db = DeviceScanAdapter(dbname=paths.device_scan_db,
                            kind='sqlite')
    db.connect()

    dbs = DeviceScanSelector(_db=db)
    dbs._execute_query()

    dbs.configure_traits()



#============= EOF =============================================
