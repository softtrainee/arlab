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
#=============enthought library imports=======================
from traits.api import HasTraits, Str, implements, Any, List
from pyface.timer.api import Timer

#=============standard library imports ========================
import random
from threading import Lock
from datetime import datetime

#=============local library imports  ==========================


#from streamable import Streamable
from viewable_device import ViewableDevice
from i_core_device import ICoreDevice
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.helpers.datetime_tools import generate_timestamp
from src.graph.time_series_graph import TimeSeriesStreamGraph

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
        
        
class CoreDevice(ViewableDevice):
    '''
    '''
    graph_klass = TimeSeriesStreamGraph

    implements(ICoreDevice)
    _communicator = None
    name = Str
    id_query = ''
    id_response = ''

    
    is_scanable = False
    scan_func = None
    scan_lock = None
    timer = None
    scan_period = 1000
    scan_units = 'ms'
    record_scan_data = True
    
    current_scan_value = 0
    
    time_dict = dict(ms=1, s=1000, m=60.0 * 1000, h=60.0 * 60.0 * 1000)
    application = Any
    
    no_response_counter = 0
    alarms = List(Alarm)
    
    def get(self):
        return self.current_scan_value
#        if self.simulation:
#            return 'simulation'

    def set(self, v):
        pass

    def _communicator_factory(self, communicator_type):
        if communicator_type is not None:

            class_key = '{}Communicator'.format(communicator_type.capitalize())
            module_path = 'src.hardware.core.communicators.{}_communicator'.format(communicator_type)
            classlist = [class_key]

            class_factory = __import__(module_path, fromlist=classlist)
            return getattr(class_factory, class_key)(name='_'.join((self.name, communicator_type)),
                          id_query=self.id_query,
                          id_response=self.id_response
                         )
            
#            gdict = globals()
#            if communicator_type in gdict:
#                return gdict[communicator_type](name='_'.join((self.name, communicator_type)),
#                                   id_query=self.id_query,
#                                   id_response=self.id_response
#                                )
    def post_initialize(self, *args, **kw):
        self.setup_scan()
        self.setup_alarms()
            
    def load(self, *args, **kw):
        '''
            Load a configuration file.  
            Get Communications info to make a new communicator
        '''
        config = self.get_configuration()
        if config:
            if config.has_section('Communications'):
                type = self.config_get(config, 'Communications', 'type')

                communicator = self._communicator_factory(type)
                if communicator is not None:
                    #give the _communicator the config object so it can load its args
                    communicator.load(config, self.config_path)

                    if hasattr(self, 'id_query'):
                        communicator.id_query = getattr(self, 'id_query')
                    self._communicator = communicator
                else:
                    return False
            #load additional child specific args
            r = self.load_additional_args(config)
            if r:
                self._loaded = True
            return r

    def load_additional_args(self, config):
        '''
        '''
        return True

    def open(self, **kw):
        '''
        '''
        if self._communicator is not None:
            return self._communicator.open(**kw)


    def ask(self, cmd, **kw):
        '''
        '''
        if self._communicator is not None:
            r = self._communicator.ask(cmd, **kw)
            self.last_command = cmd.strip()
            self.last_response = str(r)
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
            self.last_command = ' '.join(map(str, args) + map(str, kw.iteritems()))
            self.last_response = '-'
            return self._communicator.tell(*args, **kw)

    def read(self, *args, **kw):
        '''
        '''
        if self._communicator is not None:
            return self._communicator.read(*args, **kw)

    def get_random_value(self, min=0, max=10):
        '''
            convienent method for getting a random integer between min and max
            
            Defaults:
                min=0
                max=10

        '''
        return random.randint(min, max)

    def set_scheduler(self, s):
        if self._communicator is not None:
            self._communicator.scheduler = s

#===============================================================================
# streamin interface
#===============================================================================
    def setup_scan(self):
        
        
        #should get scan settings from the config file not the initialization.xml
        
        config = self.get_configuration()
        if config.has_section('Scan'):
            if config.getboolean('Scan', 'enabled'):
                self.is_scanable = True
                self.set_attribute(config, 'scan_period', 'Scan', 'period', cast='float')
                self.set_attribute(config, 'scan_units', 'Scan', 'units')
                self.set_attribute(config, 'record_scan_data', 'Scan', 'record', cast='boolean')
                
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
                v = getattr(self, self.scan_func)()
            except AttributeError, e:
                print e
                return

            if v is not None:
                self.current_scan_value = v
            
                if self.record_scan_data:
                    if isinstance(v, tuple):
                        x = self.graph.record_multiple(v)
                    else:
                        x = self.graph.record(v)
                        v = (v,)
                    
                    ts = generate_timestamp()
                    self.data_manager.write_to_frame((ts, x) + v)
                
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
                if self.no_response_counter > 3:
                    self.info('no response. stopping scan')
                    self.timer.Stop()
                    self.no_response_counter = 0
                else:
                    self.info('no response {}'.format(self.no_response_counter))
                    self.no_response_counter += 1

    def scan(self, *args, **kw):
        '''

        '''
        if self.scan_lock is None:
            self.scan_lock = Lock()

        self.scan_lock.acquire()
        self._scan_(*args, **kw)
        self.scan_lock.release()
        
    def start_scan(self):
        if self.timer is not None:
            self.timer.Stop()

#        if not self.simulation:
        self.info('Starting scan')
        if self.record_scan_data:
            self.data_manager = CSVDataManager()
            self.frame_name = self.data_manager.new_frame(base_frame_name=self.name)
        
        sp = self.scan_period * self.time_dict[self.scan_units]
        
        self.timer = Timer(sp, self.scan)
        self.timer.Start()

    def stop_scan(self):
        if self.timer is not None:
            self.timer.Stop()  

#========================= EOF ============================================
