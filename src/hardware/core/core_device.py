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

#=============enthought library imports=======================
from traits.api import HasTraits, Str, implements, Any, List, \
    Bool, Enum
#from pyface.timer.api import Timer
#=============standard library imports ========================
import random
#from threading import Lock
from datetime import datetime
#=============local library imports  ==========================
from i_core_device import ICoreDevice
#from src.helpers.timer import Timer
#from src.managers.data_managers.csv_data_manager import CSVDataManager
#from src.helpers.datetime_tools import generate_datetimestamp
from src.graph.time_series_graph import TimeSeriesStreamGraph
from src.hardware.core.scanable_device import ScanableDevice
from src.rpc.rpcable import RPCable
from src.has_communicator import HasCommunicator


class Alarm(HasTraits):
    alarm_str = Str
    triggered = False

    def get_alarm_params(self):
        als = self.alarm_str
        cond = als[0]
        if cond not in ['<', '>']:
            cond = '='
            trigger = float(als)
        else:
            trigger = float(als[1:])
        return cond, trigger

    def test_condition(self, value):
        cond, trigger = self.get_alarm_params()

        expr = 'value {} {}'.format(cond, trigger)

        triggered = eval(expr, {}, dict(value=value))

        if triggered:
            if not self.triggered:
                self.triggered = True
        else:
            self.triggered = False

        return self.triggered

    def get_message(self, value):
        cond, trigger = self.get_alarm_params()
        tstamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        return '<<<<<<ALARM {}>>>>>> {} {} {}'.format(tstamp, value, cond, trigger)


class CoreDevice(ScanableDevice, RPCable, HasCommunicator):
    '''
    '''
#    graph_klass = TimeSeriesStreamGraph

    implements(ICoreDevice)
    name = Str
#    id_query = ''
#    id_response = ''

    current_scan_value = 0

    application = Any

    _no_response_counter = 0
    alarms = List(Alarm)

    dm_kind = Enum('h5', 'csv')
    use_db = Bool(False)
    _auto_started = False

    def _communicate_hook(self, cmd, r):
        self.last_command = cmd
        self.last_response = r if r else ''

    def load(self, *args, **kw):
        '''
            Load a configuration file.  
            Get Communications info to make a new communicator
        '''
        config = self.get_configuration()
        if config:
            if config.has_section('Communications'):
                comtype = self.config_get(config, 'Communications', 'type')
                if not self._load_communicator(config, comtype):
                    return False

            self._load_hook(config)

            #load additional child specific args
            r = self.load_additional_args(config)
            if r:
                self._loaded = True
            return r

    def initialize(self, *args, **kw):
        a = super(CoreDevice, self).initialize(*args, **kw)
        b = False
        if self._communicator is not None:
            b = self._communicator.initialize(*args, **kw)

        return a and b

    def load_additional_args(self, config):
        '''
        '''
        return True

    def ask(self, cmd, **kw):
        '''
        '''
        if self._communicator is not None:
            r = self._communicator.ask(cmd, **kw)
            self._communicate_hook(cmd, r)
            return r
        else:
            self.info('no communicator for this device {}'.format(self.name))

    def write(self, *args, **kw):
        '''
        '''
        self.tell(*args, **kw)

    def tell(self, *args, **kw):
        '''
        '''
        if self._communicator is not None:
            cmd = ' '.join(map(str, args) + map(str, kw.iteritems()))
            self._communicate_hook(cmd, '-')
            return self._communicator.tell(*args, **kw)

    def read(self, *args, **kw):
        '''
        '''
        if self._communicator is not None:
            return self._communicator.read(*args, **kw)

    def get(self):
        return self.current_scan_value
#        if self.simulation:
#            return 'simulation'

    def set(self, v):
        pass



#            gdict = globals()
#            if communicator_type in gdict:
#                return gdict[communicator_type](name='_'.join((self.name, communicator_type)),
#                                   id_query=self.id_query,
#                                   id_response=self.id_response
#                                )
    def post_initialize(self, *args, **kw):
        self.setup_scan()
        self.setup_alarms()

    def get_random_value(self, mi=0, ma=10):
        '''
            convienent method for getting a random integer between min and max
            
            Defaults:
                min=0
                max=10

        '''
        return random.randint(mi, ma)

    def set_scheduler(self, s):
        if self._communicator is not None:
            self._communicator.scheduler = s
#            self._communicator._lock=s._lock
    def _parse_response(self, v):
        return v

    def repeat_command(self, cmd, ntries=2, check_val=None, check_type=None,
                       verbose=True):

        if isinstance(cmd, tuple):
            cmd = self._build_command(*cmd)
        else:
            cmd = self._build_command(cmd)

        for i in range(ntries + 1):
            resp = self._parse_response(self.ask(cmd, verbose=verbose))
            if verbose:
                m = 'repeat command {} response = {} len={} '.format(i + 1,
                                                resp,
                                                len(str(resp)) if resp is not None else None)
                self.debug(m)
            if check_val is not None:
                if self.simulation:
                    resp = check_val

                if resp == check_val:
                    break
                else:
                    continue

            if check_type is not None:
                if self.simulation:
                    resp = random.randint(1, 10)
                else:
                    try:
                        resp = check_type(resp)
                    except (ValueError, TypeError):
                        continue

            if resp is not None:
                break

        return resp

#===============================================================================
# scanable interface
#===============================================================================
    def _scan_hook(self, v):
        for a in self.alarms:
            if a.test_condition(v):
                alarm_msg = a.get_message(v)
                self.warning(alarm_msg)
                manager = self.application.get_service('src.social.twitter_manager.TwitterManager')
                if manager is not None:
                    manager.post(alarm_msg)
                break


##===============================================================================
## streamin interface
##===============================================================================
#    def setup_scan(self):
#        #should get scan settings from the config file not the initialization.xml
#
#        config = self.get_configuration()
#        if config.has_section('Scan'):
#            if config.getboolean('Scan', 'enabled'):
#                self.is_scanable = True
#                self.set_attribute(config, 'auto_start', 'Scan', 'auto_start', cast='boolean', default=True)
#                self.set_attribute(config, 'scan_period', 'Scan', 'period', cast='float')
#                self.set_attribute(config, 'scan_units', 'Scan', 'units')
#                self.set_attribute(config, 'record_scan_data', 'Scan', 'record', cast='boolean')
#                self.set_attribute(config, 'graph_scan_data', 'Scan', 'graph', cast='boolean')
#                self.set_attribute(config, 'use_db', 'DataManager', 'use_db', cast='boolean', default=False)
#                self.set_attribute(config, 'dm_kind', 'DataManager', 'kind', default='csv')
#
#    def setup_alarms(self):
#        config = self.get_configuration()
#        if config.has_section('Alarms'):
#            for opt in config.options('Alarms'):
#                self.alarms.append(Alarm(
#                                         name=opt,
#                                         alarm_str=config.get('Alarms', opt)
#                                         ))
#
#    def _scan_(self, *args):
#        '''
#
#        '''
#        if self.scan_func:
#            try:
#                v = getattr(self, self.scan_func)(verbose=False)
#            except AttributeError, e:
#                print e
#                return
#
#            if v is not None:
#                self.current_scan_value = str(v)
#
#                if self.graph_scan_data:
#                    if isinstance(v, tuple):
#                        x = self.graph.record_multiple(v)
#                    elif isinstance(v, PlotRecord):
#                        for pi, d in zip(v.plotids, v.data):
#
#                            if isinstance(d, tuple):
#                                x = self.graph.record_multiple(d, plotid=pi)
#                            else:
#                                x = self.graph.record(d, plotid=pi)
#                        v = v.as_data_tuple()
#
#                    else:
#                        x = self.graph.record(v)
#                        v = (v,)
#
#                if self.record_scan_data:
#                    if self.dm_kind == 'csv':
#                        ts = generate_datetimestamp()
#                        self.data_manager.write_to_frame((ts, x) + v)
#                    else:
#                        tab = self.data_manager.get_table('scan1', '/scans')
#                        if tab is not None:
#                            r = tab.row
#                            r['time'] = x
#                            r['value'] = v[0]
#                            r.append()
#                            tab.flush()
#
#                for a in self.alarms:
#                    if a.test_condition(v):
#
#                        alarm_msg = a.get_message(v)
#                        self.warning(alarm_msg)
#                        manager = self.application.get_service('src.social.twitter_manager.TwitterManager')
#                        if manager is not None:
#                            manager.post(alarm_msg)
#
#                        break
#
#            else:
#                '''
#                    scan func must return a value or we will stop the scan
#                    since the timer runs on the main thread any long comms timeouts
#                    slow user interaction
#                '''
#                if self._no_response_counter > 3:
#                    self.timer.Stop()
#                    self.info('no response. stopping scan')
#                    self._scanning = False
#                    self._no_response_counter = 0
#
#                else:
#                    self._no_response_counter += 1
#
#    def scan(self, *args, **kw):
#        '''
#
#        '''
#        if self.scan_lock is None:
#            self.scan_lock = Lock()
#
#        with self.scan_lock:
#            self._scan_(*args, **kw)
#
#    def start_scan(self, auto=False):
#
#        self._auto_started = auto
#
#        if self.timer is not None:
#            self.timer.Stop()
#
#        self._scanning = True
#        self.info('Starting scan')
#        if self.record_scan_data:
#            if self.dm_kind == 'h5':
#                klass = H5DataManager
#            else:
#                klass = CSVDataManager
#
#            dm = self.data_manager
#            if dm is None:
#                self.data_manager = dm = klass()
#
#            dw = DataWarehouse(root=device_scan_root)
#            dw.build_warehouse()
#
#            self.frame_name = dm.new_frame(base_frame_name=self.name,
#                                           directory=dw.get_current_dir())
#            self.scan_path = dm.get_current_path()
#
#            if self.dm_kind == 'h5':
#                g = dm.new_group('scans')
#                _t = dm.new_table(g, 'scan1')
#
#            if self.auto_start and auto:
#                self.save_scan_to_db()
#
#        sp = self.scan_period * self.time_dict[self.scan_units]
#        self.timer = Timer(sp, self.scan)
#
#    def save_scan_to_db(self):
##        p = '/Users/ross/Sandbox/device_scans.sqlite'
#        p = device_scan_db
#        db = DeviceScanAdapter(name=p,
#                               kind='sqlite')
#        db.connect(test=True)
#        dev = db.add_device(self.name, klass=self.__class__.__name__)
#        s = db.add_scan(dev)
#
#        path = self.scan_path
#        db.add_path(s, path)
#        self.info('saving scan {} to database {}'.format(path, p))
#
#        db.commit()
#
#    def stop_scan(self):
#        self._scanning = False
#        if self.timer is not None:
#            self.timer.Stop()
#
#        if self.record_scan_data and not self._auto_started:
#            if self.use_db:
#                if self.db_save_dialog():
#                    self.save_scan_to_db()
#
#        self.data_manager.close()
#
#    def _get_scan_label(self):
#        return 'Start' if not self._scanning else 'Stop'
#
#    def _scan_button_fired(self):
#        if self._scanning:
#            self.stop_scan()
#        else:
#            self.start_scan()
#
#    def _scan_period_changed(self):
#        if self._scanning:
#            self.stop_scan()
#            self.start_scan()
#========================= EOF ============================================
