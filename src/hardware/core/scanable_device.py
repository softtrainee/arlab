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
from traits.api import Event, Property, Any, Bool, Float, Str, Instance
from traitsui.api import HGroup, VGroup, Item, spring, ButtonEditor
#============= standard library imports ========================
from threading import Lock
import os
#============= local library imports  ==========================
from src.hardware.core.viewable_device import ViewableDevice
from src.graph.plot_record import PlotRecord
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.helpers.paths import device_scan_db, device_scan_root
from src.database.data_warehouse import DataWarehouse
from src.helpers.timer import Timer
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.helpers.datetime_tools import generate_datetimestamp
from src.hardware.core.alarm import Alarm
from src.graph.graph import Graph

class ScanableDevice(ViewableDevice):
    scan_button = Event
    scan_label = Property(depends_on='_scanning')
    _scanning = Bool(False)

    is_scanable = False
    scan_func = Any
    scan_lock = None
    timer = None
    scan_period = Float(1000, enter_set=True, auto_set=False)
    scan_units = 'ms'
    record_scan_data = Bool(True)
    graph_scan_data = Bool(True)
    scan_path = Str
    auto_start = Bool(False)
    scan_root = Str
    scan_name = Str

    graph_klass = Graph
    graph = Instance(Graph)

    def _scan_path_changed(self):
        self.scan_root = os.path.split(self.scan_path)[0]
        self.scan_name = os.path.basename(self.scan_path)
#===============================================================================
# streamin interface
#===============================================================================

    def setup_scan(self):
        #should get scan settings from the config file not the initialization.xml

        config = self.get_configuration()
        if config.has_section('Scan'):
            if config.getboolean('Scan', 'enabled'):
                self.is_scanable = True
                self.set_attribute(config, 'auto_start', 'Scan', 'auto_start', cast='boolean', default=True)
                self.set_attribute(config, 'scan_period', 'Scan', 'period', cast='float')
                self.set_attribute(config, 'scan_units', 'Scan', 'units')
                self.set_attribute(config, 'record_scan_data', 'Scan', 'record', cast='boolean')
                self.set_attribute(config, 'graph_scan_data', 'Scan', 'graph', cast='boolean')
                self.set_attribute(config, 'use_db', 'DataManager', 'use_db', cast='boolean', default=False)
                self.set_attribute(config, 'dm_kind', 'DataManager', 'kind', default='csv')

    def setup_alarms(self):
        config = self.get_configuration()
        if config.has_section('Alarms'):
            for opt in config.options('Alarms'):
                self.alarms.append(Alarm(
                                         name=opt,
                                         alarm_str=config.get('Alarms', opt)
                                         ))

    def _scan_(self, *args):
        '''

        '''
        if self.scan_func:
            try:
                v = getattr(self, self.scan_func)(verbose=False)
            except AttributeError, e:
                print e
                return

            if v is not None:
                self.current_scan_value = str(v)

                if self.graph_scan_data:
                    if isinstance(v, tuple):
                        x = self.graph.record_multiple(v)
                    elif isinstance(v, PlotRecord):
                        for pi, d in zip(v.plotids, v.data):

                            if isinstance(d, tuple):
                                x = self.graph.record_multiple(d, plotid=pi)
                            else:
                                x = self.graph.record(d, plotid=pi)
                        v = v.as_data_tuple()

                    else:
                        x = self.graph.record(v)
                        v = (v,)

                if self.record_scan_data:
                    if self.dm_kind == 'csv':
                        ts = generate_datetimestamp()
                        self.data_manager.write_to_frame((ts, x) + v)
                    else:
                        tab = self.data_manager.get_table('scan1', '/scans')
                        if tab is not None:
                            r = tab.row
                            r['time'] = x
                            r['value'] = v[0]
                            r.append()
                            tab.flush()

                for a in self.alarms:
                    if a.test_condition(v):

                        alarm_msg = a.get_message(v)
                        self.warning(alarm_msg)
                        manager = self.application.get_service('src.social.twitter_manager.TwitterManager')
                        if manager is not None:
                            manager.post(alarm_msg)

                        break

            else:
                '''
                    scan func must return a value or we will stop the scan
                    since the timer runs on the main thread any long comms timeouts
                    slow user interaction
                '''
                if self._no_response_counter > 3:
                    self.timer.Stop()
                    self.info('no response. stopping scan')
                    self._scanning = False
                    self._no_response_counter = 0

                else:
                    self._no_response_counter += 1

    def scan(self, *args, **kw):
        '''

        '''
        if self.scan_lock is None:
            self.scan_lock = Lock()

        with self.scan_lock:
            self._scan_(*args, **kw)

    def start_scan(self, auto=False):

        self._auto_started = auto

        if self.timer is not None:
            self.timer.Stop()

        self._scanning = True
        self.info('Starting scan')
        if self.record_scan_data:
            if self.dm_kind == 'h5':
                klass = H5DataManager
            else:
                klass = CSVDataManager

            dm = self.data_manager
            if dm is None:
                self.data_manager = dm = klass()

            dw = DataWarehouse(root=device_scan_root)
            dw.build_warehouse()

            self.frame_name = dm.new_frame(base_frame_name=self.name,
                                           directory=dw.get_current_dir())
            self.scan_path = dm.get_current_path()

            if self.dm_kind == 'h5':
                g = dm.new_group('scans')
                _t = dm.new_table(g, 'scan1')

            if self.auto_start and auto:
                self.save_scan_to_db()

        sp = self.scan_period * self.time_dict[self.scan_units]
        self.timer = Timer(sp, self.scan)

    def save_scan_to_db(self):
        from src.database.adapters.device_scan_adapter import DeviceScanAdapter
        db = DeviceScanAdapter(dbname=device_scan_db,
                               kind='sqlite')
        db.connect()
        dev = db.add_device(self.name, klass=self.__class__.__name__)
        s = db.add_scan(dev)

        path = self.scan_path
        db.add_path(s, path)
        self.info('saving scan {} to database {}'.format(path, device_scan_db))

        db.commit()

    def stop_scan(self):
        self._scanning = False
        if self.timer is not None:
            self.timer.Stop()

        if self.record_scan_data and not self._auto_started:
            if self.use_db:
                if self.db_save_dialog():
                    self.save_scan_to_db()
                else:
                    self.data_manager.delete_frame()

        self.data_manager.close()
        self._auto_started = False

    def _get_scan_label(self):
        return 'Start' if not self._scanning else 'Stop'

    def _scan_button_fired(self):
        if self._scanning:
            self.stop_scan()
        else:
            self.start_scan()

    def _scan_period_changed(self):
        if self._scanning:
            self.stop_scan()
            self.start_scan()

    def _graph_default(self):

        g = self.graph_klass(
                  container_dict=dict(padding=[10, 10, 10, 10])
                  )

        self.graph_builder(g)

        return g

    def graph_builder(self, g, **kw):

        g.new_plot(padding=[40, 5, 5, 20],
                   zoom=True,
                  pan=True,
                  **kw
                   )
        g.new_series()

    def current_state_view(self):
        g = VGroup(Item('graph', show_label=False, style='custom'),
                        VGroup(Item('scan_func', label='Function', style='readonly'),

                               HGroup(Item('scan_period', label='Period ({})'.format(self.scan_units),
                                            #style='readonly'
                                            ), spring),
                                 Item('current_scan_value', style='readonly'),
                               ),

                        VGroup(
                               HGroup(Item('scan_button', editor=ButtonEditor(label_value='scan_label'),
                                     show_label=False),
                                      spring
                                      ),
                               Item('scan_root',
                                    style='readonly',
                                    label='Scan directory',
                                    visible_when='object.record_scan_data'),
                               Item('scan_name', label='Scan name',
                                    style='readonly',
                                    visible_when='object.record_scan_data'),
                               visible_when='object.is_scanable'),

                        label='Scan'
                        )
        v = super(ScanableDevice, self).current_state_view()
        v.content.content.append(g)
        return v
#============= EOF =============================================
