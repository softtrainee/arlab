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
from traits.api import Instance, Bool, Int, Button, Event, Float, Str, String, Property, List, on_trait_change
from traitsui.api import View, Item, HGroup, VGroup, spring, ButtonEditor, EnumEditor
#============= standard library imports ========================
import numpy as np
#============= local library imports  ==========================
from src.managers.manager import Manager, ManagerHandler
from threading import Thread
from src.hardware.bakeout_controller import BakeoutController, DUTY_CYCLE
from src.hardware.core.communicators.rs485_scheduler import RS485Scheduler
import os
from src.helpers.paths import bakeout_config_dir, data_dir
from src.graph.time_series_graph import TimeSeriesStreamGraph, TimeSeriesGraph
from src.helpers.datetime_tools import generate_datestamp
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.hardware.core.i_core_device import ICoreDevice


class BakeoutManager(Manager):
    '''
    '''
    graph = Instance(TimeSeriesStreamGraph)

    bakeout1 = Instance(BakeoutController)
    bakeout2 = Instance(BakeoutController)
    bakeout3 = Instance(BakeoutController)
    bakeout4 = Instance(BakeoutController)
    bakeout5 = Instance(BakeoutController)
    bakeout6 = Instance(BakeoutController)
    
    update_interval = Float(2)
    scan_window = Int(10)
    execute = Event
    save = Button
    execute_label = Property(depends_on='alive')
    alive = Bool(False)

    configurations = Property(depends_on='_configurations')
    _configurations = List
    configuration = Property(depends_on='_configuration')
    _configuration = String
    
    buffer = List
    buffer2 = List
    data_name = Str
    n_active_controllers = 0
    active_controllers = List

    open = Button

    def load(self, *args, **kw):
        app = self.application
        for bo in self._get_controllers():
            bc = self._controller_factory(bo)
            self.trait_set(**{bo:bc})

        if app is not None:
            app.register_service(ICoreDevice, bc)


    @on_trait_change('bakeout+:process_value_flag')
    def update_graph_temperature(self, obj, name, old, new):
        if obj.isAlive():
            id = self.graph_info[obj.name]['id']
            
            datum = getattr(obj, 'process_value')
            self.graph.record(datum, series=id)
            if obj.name not in self.buffer:
                self.buffer.append(obj.name)

            if len(self.buffer) == len(self.active_controllers):
                self.write_data(self.data_name)
                self.buffer = []

    @on_trait_change('bakeout+:duty_cycle')
    def update_graph_duty_cycle(self, obj, name, old, new):
        if DUTY_CYCLE:
            if obj.isAlive():
                id = self.graph_info[obj.name]['id']
                self.graph.record(new, series=id, plotid=1)
                if obj.name not in self.buffer2:
                    self.buffer2.append(obj.name)

                if len(self.buffer2) == len(self.active_controllers):
                    self.write_data(self.data_name2, plotid=1)
                    self.buffer2 = []

    def write_data(self, name, plotid=0):
        p = self.data_manager.frames[name]
        h = []
        for c in self.active_controllers:
            h.append('%s_time' % c)
            h.append('%s_temp' % c)

        self.graph.export_raw_data(header=h, path=p, plotid=plotid)

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
        scheduler = RS485Scheduler(collision_delay=150)
        for bcn in self._get_controllers():
            bc = getattr(self, bcn)
            #set the communicators scheduler
            #used to synchronize access to port
            if bc.load():
                if bc.open():
                    bc.set_scheduler(scheduler)
                    bc.initialize()

#            self.trait_set(**{'bakeout%i' % (i + 1):bc})

        self._load_configurations()
        return True

    def _controller_factory(self, name):
        bc = BakeoutController(name=name,
                                   configuration_dir_name='bakeout',
                                   logger_display=self.logger_display,
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
        g = self._graph_factory(stream=False, **dict(pan=True, zoom=True))#graph = self.graph)
        #p = '/Users/Ross/Pychrondata_beta/data/bakeouts/bakeout-2011-02-17008.txt'

        self._parse_graph_file(g, path)

        if DUTY_CYCLE:
            head, tail = os.path.split(path)
            args = tail.split('-')
            name = args[0]
            date = '-'.join(args[1:])
            name = '.%s_duty_cycle-%s' % (name, date)
            path = os.path.join(head, name)
            self._parse_graph_file(g, path, plotid=1)

        g.window_title = os.path.basename(path)
        g.edit_traits()

    def _parse_graph_file(self, graph, path, plotid=0):
        import csv

        reader = csv.reader(open(path, 'r'))
        header = reader.next()
        nseries = len(header) / 2
        for i in range(nseries):

            #set up graph
            name = header[2 * i][:-5]
            graph.new_series(type='line', render_style='connectedpoints', plotid=plotid)
            #self.graph_info[name] = dict(id = i)

            graph.set_series_label(name, series=i, plotid=plotid)

        data = np.array_split(np.array([row for row in reader], dtype=float), nseries, axis=1)
        for i, da in enumerate(data):
            x, y = np.transpose(da)

            graph.set_data(x, series=i, axis=0, plotid=plotid)
            graph.set_data(y, series=i, axis=1, plotid=plotid)


    def _open_fired(self):
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
                if script is not '---':
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
            id = 0
            #self.n_active_controllers = 0
            self.active_controllers = []
            self.graph_info = dict()
            self._graph_factory(graph=self.graph)
            #setup data recording
            self.data_manager = dm = CSVDataManager()

            name = 'bakeout-%s' % generate_datestamp()
            self.data_name = dm.new_frame(directory='bakeouts',
                         base_frame_name=name)

#            if DUTY_CYCLE:
#                self.data_name2 = name = '.bakeout_duty_cycle-%s' % generate_datestamp()
#                dm.new_frame(None, directory='bakeouts',
#                             base_frame_name=name)
            #clear_ids = []
            #names = []
            for tr in self._get_controllers():
                bc = self.trait_get(tr)[tr]
                if bc.ok_to_run():
                    bc.on_trait_change(self.update_alive, 'alive')

                    #set up graph
                    self.graph.new_series(type='line', render_style='connectedpoints')
                    self.graph_info[bc.name] = dict(id=id)

                    self.graph.set_series_label(tr, series=id)

                    #setup duty cycle subgraph
#                    if DUTY_CYCLE:
#                        self.graph.new_series(type='line', render_style='connectedpoints',
#                                              plotid=1)
                    #clear_ids.append('plot%i' % (id))



                    t = Thread(target=bc.run)
                    t.start()

                    id += 1
                    self.active_controllers.append(tr)
                    #names.append(tr)

            #self.graph.clear_legend(clear_ids)

    def _update_interval_changed(self):
        for tr in self._get_controllers():
            bc = self.trait_get(tr)[tr]
            bc.update_interval = self.update_interval
            
        self.graph.set_scan_delay(self.update_interval)
        
#============= views ===================================
    def traits_view(self):
        '''
        '''
        controller_grp = HGroup(
                   )
        for tr in self._get_controllers():
            controller_grp.content.append(Item(tr, show_label=False, style='custom'))

        control = HGroup(VGroup(
                         Item('execute', editor=ButtonEditor(label_value='execute_label'),
                              show_label=False),
                         Item('open', show_label=False)),
                        spring,
                        HGroup(Item('configuration', editor=EnumEditor(name='configurations'),
                             show_label=False),
                             Item('save', show_label=False),

                             ),
                         
                         
                        )
        
        v = View(VGroup(control,
                        Item('update_interval'),
                        Item('scan_window'),
                        controller_grp, Item('graph', show_label=False, style='custom')),
               handler=ManagerHandler,
               resizable=True,
               title='Bakeout Manager')
        return v

    def _get_controllers(self):
        '''
        '''
        c = [tr for tr in self.traits() if tr.startswith('bakeout')]
        c.sort()
        return c

    def _load_configurations(self):
        '''
        '''
        self._configurations = ['---']
        for p in os.listdir(bakeout_config_dir):
            if os.path.splitext(p)[1] == '.cfg':
                self._configurations.append(os.path.join(bakeout_config_dir, p))

    def _parse_config_file(self, p):
        config = self.get_configuration(p)
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
                graph = TimeSeriesStreamGraph()
            else:
                graph = TimeSeriesGraph()

        graph.clear()

        graph.new_plot(data_limit=self.scan_window / self.update_interval,
                       scan_delay=self.update_interval,
                       show_legend='ll',
                       #track_amount=1200,
                       **kw
                       )
#        if DUTY_CYCLE:
#            graph.new_plot(data_limit=3600,
#                           scan_delay=5,
#                           **kw
#                           )
#            graph.set_y_limits(min=0, max=100, plotid=1)
#            graph.set_y_title('Duty Cycle %', plotid=1)
        graph.set_x_title('Time')
        graph.set_y_title('Temp C')
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
