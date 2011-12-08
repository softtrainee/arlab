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
#============= enthought library imports =======================
from traits.api import Array, Instance, Bool, Button, Event, Float, Str, String, Property, List, on_trait_change
from traitsui.api import View, Item, HGroup, VGroup, spring, ButtonEditor, EnumEditor
#============= standard library imports ========================
import numpy as np
import os
import time
from threading import Thread
#============= local library imports  ==========================
from src.managers.manager import Manager, ManagerHandler
from src.hardware.bakeout_controller import BakeoutController
from src.hardware.core.communicators.rs485_scheduler import RS485Scheduler
from src.helpers.paths import bakeout_config_dir, data_dir
from src.graph.time_series_graph import TimeSeriesStackedGraph, \
    TimeSeriesStreamStackedGraph
from src.helpers.datetime_tools import generate_datestamp
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.hardware.core.i_core_device import ICoreDevice
from src.graph.graph import Graph
from src.hardware.core.core_device import CoreDevice
from src.hardware.gauges.granville_phillips.micro_ion_controller import MicroIonController

BATCH_SET_BAUDRATE = False
BAUDRATE = '38400'
class BakeoutManager(Manager):
    '''
    '''
    graph = Instance(Graph)
    bakeout1 = Instance(BakeoutController)
    bakeout2 = Instance(BakeoutController)
    bakeout3 = Instance(BakeoutController)
    bakeout4 = Instance(BakeoutController)
    bakeout5 = Instance(BakeoutController)
    bakeout6 = Instance(BakeoutController)
    
    update_interval = Float(2)
    scan_window = Float(10)
    #scan_window = Float(0.25)
    
    execute = Event
    save = Button
    execute_label = Property(depends_on='alive')
    alive = Bool(False)

    configurations = Property(depends_on='_configurations')
    _configurations = List
    configuration = Property(depends_on='_configuration')
    _configuration = String
    
    data_buffer = List
    data_buffer_x = List
    
    data_name = Str
    data_count_flag = 0
#    n_active_controllers = 0
    active_controllers = Property(List)
    
    open_button = Button
    open_label = 'Open'
    gauge_controller = Instance(CoreDevice)
    
    
    use_pressure_monitor = Bool(False)
    _pressure_sampling_period = 2
    _max_duration = 10 #10 hrs
    _pressure_monitor_std_threshold = 1
    _pressure_monitor_threshold = 1e-2
    _pressure = Float
    
    pressure_buffer = Array
    
    def load(self, *args, **kw):
        app = self.application
        for bo in self._get_controllers():
            bc = self._controller_factory(bo)
            self.trait_set(**{bo:bc})
                
            if app is not None:
                app.register_service(ICoreDevice, bc, {'display':False})
                
        if app is not None:
            self.gauge_controller = app.get_service(MicroIonController, query='name=="roughing_gauge_controller"')
        else:
            
            gc = MicroIonController(name='roughing_gauge_controller')
            gc.bootstrap()
            self.gauge_controller = gc
                    
    @on_trait_change('bakeout+:process_value_flag')
    def update_graph_temperature(self, obj, name, old, new):
        if obj.isAlive():
            pid = self.graph_info[obj.name]['id']
            
            pv = getattr(obj, 'process_value')
            hp = getattr(obj, 'heat_power_value')
                
            self.data_buffer.append((pid, pv, hp))
            self.data_count_flag += 1
                

            n = self.data_count_flag
            if n == len(self.active_controllers):
                for i, pi, hi in self.data_buffer:
                
                    nx = self.graph.record(pi, series=i,
                                           track_x=False,
                                           track_y=False
                                           )
                    self.graph.record(hi, x=nx, series=i, plotid=1,
                                      track_x=i == n - 1,
                                      track_y=False
                                      )
                
                    self.data_buffer_x.append(nx)
                      
                self.graph.update_y_limits(plotid=0)
                self.graph.update_y_limits(plotid=1)
            
                self.get_pressure(nx)
                self.write_data(self.data_name)
                self.data_buffer = []
                self.data_buffer_x = []
                self.data_count_flag = 0
                
    def get_pressure(self, x):
        self._pressure = pressure = self.gauge_controller.get_ion_pressure()
        self.graph.record(pressure, x=x, track_y=(5e-3, None), track_y_pad=5e-3, track_x=False, plotid=2, do_later=10)
        
        if self.use_pressure_monitor:
            dbuffer = self.pressure_buffer
            window = 100
            
            dbuffer = np.hstack((dbuffer[-window:], pressure))
            n = len(dbuffer)
            std = dbuffer.std()
            mean = dbuffer.mean()
            if std < self._pressure_monitor_std_threshold:
                if mean < self._pressure_monitor_threshold:
                    self.info('pressure set point achieved:mean={} std={} n={}'.format(mean, std, n))
            
            dtime = self._start_time - time.time()
            if dtime > self._max_duration:
                for ac in self._get_active_controllers():
                    error = 'Max duration exceeded max={:0.1f}, dur={:0.1f}'.format(self._max_duration, dtime)
                    ac.end(error=error)
            
    def write_data(self, name, plotid=0):
        datum = []
        for sub, x in zip(self.data_buffer, self.data_buffer_x):
            _pid, pi, hp = sub
            datum.append(x)
            datum.append(pi)
            datum.append(hp)
        
        datum.append(self._pressure)
            
        self.data_manager.write_to_frame(datum)

    def update_alive(self, obj, name, old, new):
        if new:
            self.alive = new
        else:
            self.alive = self.isAlive()

    def isAlive(self):
        for tr in self._get_controllers():
            tr = getattr(self, tr)
            if tr.isActive() and tr.isAlive():
                return True

        return False

    def load_controllers(self):
        '''
        '''
        scheduler = RS485Scheduler()
        for bcn in self._get_controllers():
            bc = getattr(self, bcn)
            #set the communicators scheduler
            #used to synchronize access to port
            if bc.load():
                if bc.open():
                    bc.set_scheduler(scheduler)
                    bc.initialize()
                    
#                    if BATCH_SET_BAUDRATE:
#                        bc.set_baudrate(BAUDRATE)
                    

        self._load_configurations()
        return True

    def _controller_factory(self, name):
        bc = BakeoutController(name=name,
                                   configuration_dir_name='bakeout',
                                   #logger_display=self.logger_display,
                                   update_interval=self.update_interval
                                   )
        return bc
    
    def kill(self, **kw):
        '''
        '''
        if 'user_kill' in kw:
            if not kw['user_kill']:
                super(BakeoutManager, self).kill()
        else:
            super(BakeoutManager, self).kill()

        for tr in self._get_controllers():
            getattr(self, tr).end(**kw)

    def _open_graph(self, path):
        g = self._graph_factory(stream=False, **dict(pan=True, zoom=True))
        #p = '/Users/Ross/Pychrondata_beta/data/bakeouts/bakeout-2011-02-17008.txt'

        self._parse_graph_file(g, path)
        g.window_title = name = os.path.basename(path)
        
        name, _ext = os.path.splitext(name)
        g.set_title(name)
        g.window_width = 0.66
        g.window_height = 0.85
        g.window_x = 30
        g.window_y = 30
        g.edit_traits()

    def _parse_graph_file(self, graph, path, plotid=0):
        import csv

        reader = csv.reader(open(path, 'r'))
        header = reader.next()
        nseries = len(header) / 3
        for i in range(nseries):

            #set up graph
            name = header[2 * i][:-5]
            graph.new_series(type='line', render_style='connectedpoints', plotid=plotid)
            graph.new_series(type='line', render_style='connectedpoints', plotid=plotid + 1)
            #self.graph_info[name] = dict(id = i)

            graph.set_series_label(name, series=i, plotid=plotid)
        
        data = np.array_split(np.array([row for row in reader], dtype=float), nseries, axis=1)
        for i, da in enumerate(data):
            x, y, h = np.transpose(da)

            graph.set_data(x, series=i, axis=0, plotid=plotid)
            graph.set_data(y, series=i, axis=1, plotid=plotid)
            
            graph.set_data(x, series=i, axis=0, plotid=plotid + 1)
            graph.set_data(h, series=i, axis=1, plotid=plotid + 1)

    def _open_button_fired(self):
        path = self._file_dialog_('open', default_directory=os.path.join(data_dir, 'bakeouts'))
        if path is not None:
            self._open_graph(path)

    def _save_fired(self):

        path = self._file_dialog_('save as', default_directory=bakeout_config_dir)
        if path is not None:
            config = self.get_configuration_writer()

            for tr in self._get_controllers():
                tr_obj = getattr(self, tr)
                config.add_section(tr)
                
                script = getattr(tr_obj, 'script')
                if script != '---':
                    config.set(tr, 'script', script)
                else:
                    for attr in ['duration', 'setpoint']:
                        config.set(tr, attr, getattr(tr_obj, attr))

            with open(path, 'w') as f:
                config.write(f)
                
            self._set_configuration(path)
            self._load_configurations()

    def _execute_fired(self):
        '''
        '''
        if self.isAlive():
            self.kill(user_kill=True)
        else:
            pid = 0
            header = []
            self.data_buffer = []
            self.data_buffer_x = []
            self.data_count_flag = 0
            self.graph_info = dict()
            self._graph_factory(graph=self.graph)

        
            set_dm = True
            _alive = False
            for name in self._get_controllers():
                bc = self.trait_get(name)[name]
                if bc.ok_to_run():
                    _alive = True
                    if set_dm:
                        #setup data recording
                        self.data_manager = dm = CSVDataManager()
            
                        ni = 'bakeout-{}'.format(generate_datestamp())
                        self.data_name = dm.new_frame(directory='bakeouts',
                                     base_frame_name=ni)
                        set_dm = False
                        
                    bc.on_trait_change(self.update_alive, 'alive')

                    #set up graph
                    self.graph.new_series(type='line', render_style='connectedpoints')
                    self.graph_info[bc.name] = dict(id=pid)

                    self.graph.set_series_label(name, series=pid)

                    self.graph.new_series(type='line', render_style='connectedpoints',
                                          plotid=1)
                    
            
                    t = Thread(target=bc.run)
                    t.start()
                    
                    if pid == 0:
                        header.append('#{}_time'.format(name))
                    else:
                        header.append('{}_time'.format(name))
                    header.append('{}_temp'.format(name))
                    header.append('{}_heat_power'.format(name))
                    pid += 1
            
            if _alive:
                
                #pressure plot
                self.graph.new_series(type='line', render_style='connectedpoints',
                                  plotid=2)
                header.append('pressure')
                self._start_time = time.time()
                #start a pressure monitor thread
#                t = Thread(target=self._pressure_monitor)
#                t.start()
                    
            
                #set the header in for the data file
                self.data_manager.write_to_frame(header)    

            
#    def _pressure_monitor(self):
#    
#        window = 100
#
#        st = time.time()
#       
#        
#        dbuffer = np.array([])
#        
#        success = False
#        while time.time() - st < self._max_duration * 60 * 60:
#            
#            nv = self.gauge_controller.get_convectron_a_pressure()
#            self._pressure = nv
#            self.graph.record(nv, track_y=(5e-3, None), track_y_pad=5e-3, track_x=False, plotid=2, do_later=10)
#
#            if self.use_pressure_monitor:
#                dbuffer = np.hstack((dbuffer[-window:], nv))
#                n = len(dbuffer)
#                std = dbuffer.std()
#                mean = dbuffer.mean()
#                if std < self._pressure_monitor_std_threshold:
#                    if mean < self._pressure_monitor_threshold:
#                        self.info('pressure set point achieved:mean={} std={} n={}'.format(mean, std, n))
#                        success = True
#                        break
#                    
#            time.sleep(self._pressure_sampling_period)
#            if not self.isAlive():
#                break
#        
#        for ac in self._get_active_controllers():
#            ac.end(error=None if success else 'Max duration exceeded max={:0.1f}, dur={:0.1f}'.format(self._max_duration,
#                                                                                                               time.time() - st))

    def _update_interval_changed(self):
        for tr in self._get_controllers():
            bc = self.trait_get(tr)[tr]
            bc.update_interval = self.update_interval
            
        self.graph.set_scan_delay(self.update_interval)
        
#============= views ===================================
    def traits_view(self):
        '''
        '''
        controller_grp = HGroup()
        for tr in self._get_controllers():
            controller_grp.content.append(Item(tr, show_label=False, style='custom'))

        control_grp = HGroup(VGroup(
                         Item('execute', editor=ButtonEditor(label_value='execute_label'),
                              show_label=False),
                         Item('open_button', editor=ButtonEditor(label_value='open_label'),
                              show_label=False)
                                ),
#                        spring,
                        HGroup(Item('configuration', editor=EnumEditor(name='configurations'),
                             show_label=False),
                             Item('save', show_label=False),

                             ),
                        label='Control',
                        show_border=True
                        )
        scan_grp = VGroup(Item('update_interval', label='Sample Period (s)'),
                          Item('scan_window', label='Data Window (mins)'),
                          label='Scan',
                          show_border=True
                          )
        
        pressure_grp = VGroup(
                            HGroup(
                                   Item('use_pressure_monitor'),
                                   Item('_pressure_sampling_period', label='Sample Period (s)')
                                   ),
                            VGroup(
                                   Item('_max_duration', label='Max. Duration (hrs)'),
                                   Item('_pressure_monitor_std_threshold'),
                                   Item('_pressure_monitor_threshold'),
                                   enabled_when='use_pressure_monitor'
                                   ),
                            label='Pressure',
                            show_border=True
                            )
        v = View(VGroup(
                        HGroup(control_grp,
                               HGroup(
                                   scan_grp,
                                   pressure_grp,
#                                   spring,
                                   enabled_when='not alive')
                               ),
                        controller_grp,
                        Item('graph', show_label=False, style='custom')
                        ),
               handler=ManagerHandler,
               resizable=True,
               title='Bakeout Manager',
               height=830
               )
        return v

    def _get_controllers(self):
        '''
        '''
        c = [tr for tr in self.traits() if tr.startswith('bakeout')]
        c.sort()
        return c
    
    def _get_active_controllers(self):
        ac = []
        for tr in self._get_controllers():
            tr = getattr(self, tr)
            if tr.isActive() and tr.isAlive():
                ac.append(tr)
        return ac

    def _load_configurations(self):
        '''
        '''
        self._configurations = ['---']
        for p in os.listdir(bakeout_config_dir):
            if os.path.splitext(p)[1] == '.cfg':
                self._configurations.append(os.path.join(bakeout_config_dir, p))

    def _parse_config_file(self, p):
        config = self.get_configuration(p, warn=False)
        if config is None:
            return 
        for section in config.sections():
            kw = dict()
            script = self.config_get(config, section, 'script', optional=True)
            if script:
                kw['script'] = script
            else:
                kw['script'] = '---'     
                for opt in ['duration', 'setpoint']:
                    value = self.config_get(config, section, opt, cast='float')
                    if value is not None:
                        kw[opt] = value
            getattr(self, section).trait_set(**kw)

    def _get_configurations(self):
        return [os.path.basename(p) for p in self._configurations]

    def _get_configuration(self):
        return os.path.splitext(os.path.basename(self._configuration))[0]

    def _set_configuration(self, c):
        self._configuration = os.path.join(bakeout_config_dir, c)

    def _get_execute_label(self):
        return 'Stop' if self.alive else 'Execute'

    def __configuration_changed(self):
        for tr in self._get_controllers():
            kw = dict()
            tr_obj = getattr(self, tr)
            for attr in ['duration', 'setpoint']:
                kw[attr] = 0
            kw['script'] = '---'
            tr_obj.trait_set(**kw)
        
        if self.configuration is not '---':
            self._parse_config_file(self._configuration)   

    def _graph_factory(self, stream=True, graph=None, **kw):
        if graph is None:
            if stream:
                graph = TimeSeriesStreamStackedGraph(panel_height=145)
            else:
                graph = TimeSeriesStackedGraph(panel_height=300)
        graph.clear()
        kw['data_limit'] = self.scan_window * 60 / self.update_interval
        kw['scan_delay'] = self.update_interval
        #temps
        graph.new_plot(show_legend='ll', **kw)
        
        #heat power
        graph.new_plot(**kw)
        
        #pressure
        graph.new_plot(**kw)
        
        graph.set_x_title('Time')
        graph.set_y_title('Temp (C)')
        graph.set_x_limits(0, self.scan_window * 60)
        
        graph.set_y_title('Heat Power (%)', plotid=1)
        graph.set_y_title('Pressure (torr)', plotid=2)
                
        return graph

    def _graph_default(self):
        g = self._graph_factory()
        return g


def launch_bakeout():
    b = BakeoutManager()
    b.load()
    b.load_controllers()
    
    b.configure_traits()

#============= EOF ====================================
