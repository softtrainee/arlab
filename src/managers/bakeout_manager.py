#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from traits.api import HasTraits, Array, Instance, Bool, Button, Event, \
    Float, Str, String, Property, List, on_trait_change
from traitsui.api import View, Item, HGroup, VGroup, spring, \
    ButtonEditor, EnumEditor

import numpy as np
import os
import time
from threading import Thread, Lock

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
from ConfigParser import NoSectionError
from src.managers.script_manager import ScriptManager

BATCH_SET_BAUDRATE = False
BAUDRATE = '38400'

from wx import GetDisplaySize
DISPLAYSIZE = GetDisplaySize()


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

    # scan_window = Float(0.25)

    execute = Event
    save = Button
    edit_scripts_button = Button('Edit Scripts')

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
    _max_duration = 10  # 10 hrs
    _pressure_monitor_std_threshold = 1
    _pressure_monitor_threshold = 1e-2
    _pressure = Float

    pressure_buffer = Array

    include_pressure = Bool
    include_heat = Bool(True)
    include_temp = Bool(True)

    plotids = List([0, 1, 2])

    execute_ok = Property

    script_editor = Instance(ScriptManager)

    _nactivated_controllers = 0

    def _script_editor_default(self):
        m = ScriptManager(kind='Bakeout')
        return m

    def _get_execute_ok(self):
        return sum(map(int, [self.include_temp, self.include_heat,
                   self.include_pressure])) > 0

    def load(self, *args, **kw):
        app = self.application
        for bo in self._get_controller_names():
            bc = self._controller_factory(bo)
            self.trait_set(**{bo: bc})

            if app is not None:
                app.register_service(ICoreDevice, bc, {'display'
                        : False})

        if app is not None:
            self.gauge_controller = app.get_service(MicroIonController,
                    query='name=="roughing_gauge_controller"')
        else:

            gc = MicroIonController(name='roughing_gauge_controller')
            gc.bootstrap()
            self.gauge_controller = gc

    @on_trait_change('bakeout+:process_value_flag')
    def update_graph_temperature(
        self,
        obj,
        name,
        old,
        new,
        ):
        if obj.isAlive():
            pid = self.graph_info[obj.name]['id']

            pv = getattr(obj, 'process_value')
            hp = getattr(obj, 'heat_power_value')
            with self._buffer_lock:
                self.data_buffer.append((pid, pv, hp))
                self.info('adding {} {} {}'.format(obj.name, pid, pv))
                
                self.data_count_flag += 1
                
                n = self.data_count_flag
                if n >= len(self.active_controllers):
                    #with self._buffer_lock:
                    for (i, pi, hi) in self.data_buffer:
#                        self.info('recording {} {}'.format(i,pi))
                        track_x = i == n - 1
                        if self.include_temp:
                            nx = self.graph.record(pi, series=i,
                                    track_x=track_x, track_y=False,
                                    plotid=self.plotids[0])
    
                        track_x = False
                        if self.include_heat:
                            self.graph.record(
                                hi,
                                x=nx,
                                series=i,
                                plotid=self.plotids[1],
                                track_x=track_x,
                                track_y=False,
                                )
                        self.data_buffer_x.append(nx)
                    try:
                        self.graph.update_y_limits(plotid=self.plotids[0])
                        self.graph.update_y_limits(plotid=self.plotids[1])
                    except IndexError:
                        pass
    
                    if self.include_pressure:
                        self.get_pressure(nx)
    
                    #with self._buffer_lock:
                    self.write_data()

                    self.data_buffer = []
                    self.data_buffer_x = []
                    self.data_count_flag = 0

    def get_pressure(self, x):
        if self.gauge_controller:
            pressure = self.gauge_controller.get_ion_pressure()
        else:
            import random
            pressure = random.randint(0, 10)

        self._pressure = pressure
        self.graph.record(
            pressure,
            x=x,
            track_y=(5e-3, None),
            track_y_pad=5e-3,
            track_x=False,
            plotid=self.plotids[2],
            do_later=10,
            )

        if self.use_pressure_monitor:
            dbuffer = self.pressure_buffer
            window = 100

            dbuffer = np.hstack((dbuffer[-window:], pressure))
            n = len(dbuffer)
            std = dbuffer.std()
            mean = dbuffer.mean()
            if std < self._pressure_monitor_std_threshold:
                if mean < self._pressure_monitor_threshold:
                    self.info('pressure set point achieved:mean={} std={} n={}'.format(mean,
                              std, n))

            dtime = self._start_time - time.time()
            if dtime > self._max_duration:
                for ac in self._get_active_controllers():
                    error = \
                        'Max duration exceeded max={:0.1f}, dur={:0.1f}'.format(self._max_duration,
                            dtime)
                    ac.end(error=error)

    def write_data(self):

        ns = sum(map(int, [self.include_heat,
                           self.include_pressure, self.include_temp])) + 1
        container = [0, ] * ns * self._nactivated_controllers

        for (sub, x) in zip(self.data_buffer, self.data_buffer_x):
            s = 1
            (pid, pi, hp) = sub

            ind = pid * ns
            container[ind] = x

            if self.include_temp:
                container[ind + s] = pi
                s += 1

            if self.include_heat:
                container[ind + s] = hp
                s += 1

            if self.include_pressure:
                container[ind + s] = self._pressure

        for i in range(self._nactivated_controllers):
            ind = i * ns
            if container[ind] < 0.001:
                container[ind] = x

        self.data_manager.write_to_frame(container)

    def update_alive(
        self,
        obj,
        name,
        old,
        new,
        ):
#        print obj, name, old, new
        if new:
            self.alive = new
        else:
            self.alive = bool(len(self._get_active_controllers()))#self.isAlive()

#    def isAlive(self):
##        for tr in self._get_controller_names():
##        
##            tr = getattr(self, tr)
##            if tr.isActive() and tr.isAlive():
##                return True
##
##        return False
#        return
#    
    def load_controllers(self):
        '''
        '''

        scheduler = RS485Scheduler()
        program = False
        cnt = 0
#        for bcn in self._get_controller_names():
#            bc = getattr(self, bcn)
        for bc in self._get_controllers():
            # set the communicators scheduler
            # used to synchronize access to port
            if bc.load():
                bc.set_scheduler(scheduler)

                if bc.open():

                    # on first controller check to see if memory block programming is required
                    # if it is apply to all subsequent controllers

                    if cnt == 0:
                        if not bc.is_programmed():
                            program = True
                        self.info('Watlow controllers require programming. Programming automatically' if program else
                                  'Watlow controllers are properly programmed'
                                  )

                    bc.program_memory_blocks = program

                    bc.initialize()
                    cnt += 1

#                    if BATCH_SET_BAUDRATE:
#                        bc.set_baudrate(BAUDRATE)

        self._load_configurations()
        return True

    def _controller_factory(self, name):
        bc = BakeoutController(name=name,
                               configuration_dir_name='bakeout',
                               update_interval=self.update_interval)  # logger_display=self.logger_display,
        return bc

    def kill(self, **kw):
        '''
        '''

        if 'user_kill' in kw:
            if not kw['user_kill']:
                super(BakeoutManager, self).kill()
        else:
            super(BakeoutManager, self).kill()

        for tr in self._get_controller_names():
            getattr(self, tr).end(**kw)

    def _open_graph(self, path):

        graph = self.bakeout_factory(ph=0.65,
                *self.bakeout_parser(path),
                container_dict=dict(bgcolor='red',
                                    fill_bg=True,
                                    padding_top=60
                                    )
                )

        graph.window_width = 0.66
        graph.window_height = 0.85
        graph.window_x = 30
        graph.window_y = 30
        graph.edit_traits()

    def _edit_scripts_button_fired(self):
        se = self.script_editor
        if se.save_path:
            se.title = 'Script Editor {}'.format(se.save_path)

        se.edit_traits(kind='livemodal')

        for ci in self._get_controllers():
            ci.load_scripts()

    def _open_button_fired(self):
        path = self._file_dialog_('open',
                                  default_directory=os.path.join(data_dir,
                                  'bakeouts'))
#        path = '/Users/ross/Desktop/bakeout-2012-03-16027.txt'
#        path = '/Users/ross/Desktop/bakeout-test.txt'
        if path is not None:
            self._open_graph(path)
#        self._open_graph(None)

    def _save_fired(self):

        path = self._file_dialog_('save as',
                                  default_directory=bakeout_config_dir)
        if path is not None:
            config = self.get_configuration_writer()
            config.add_section('Include')
            config.set('Include', 'temp', self.include_temp)
            config.set('Include', 'heat', self.include_heat)
            config.set('Include', 'pressure', self.include_pressure)

            config.add_section('Scan')
            config.set('Scan', 'interval', self.update_interval)
            config.set('Scan', 'window', self.scan_window)

            for tr in self._get_controller_names():
                tr_obj = getattr(self, tr)
                config.add_section(tr)

                script = getattr(tr_obj, 'script')
                if script != '---':
                    config.set(tr, 'script', script)
                else:
                    for attr in ['duration', 'setpoint', 'record_process']:
                        config.set(tr, attr, getattr(tr_obj, attr))

            with open(path, 'w') as f:
                config.write(f)

            self._set_configuration(path)
            self._load_configurations()

    def _execute_fired(self):
        t = Thread(target=self._execute_)
        t.start()

    def _execute_(self):
        '''
        '''
        self._buffer_lock = Lock()

        if self.alive:
            self.kill(user_kill=True)
            self.alive = False
        else:
            self.alive = True
            pid = 0
            header = []
            self.data_buffer = []
            self.data_buffer_x = []
            self.data_count_flag = 0
            self.graph_info = dict()
            self._graph_factory(graph=self.graph)
            controllers = []
            for name in self._get_controller_names():
                bc = self.trait_get(name)[name]
                if bc.ok_to_run():

                    bc.on_trait_change(self.update_alive, 'alive')

                    # set up graph
                    self.graph.new_series()
                    self.graph_info[bc.name] = dict(id=pid)

                    self.graph.set_series_label(name, series=pid)

                    if self.include_heat:
                        self.graph.new_series(plotid=self.plotids[1])

                    if pid == 0:
                        header.append('#{}_time'.format(name))
                    else:
                        header.append('{}_time'.format(name))

                    if self.include_temp:
                        header.append('{}_temp'.format(name))

                    if self.include_heat:
                        header.append('{}_heat_power'.format(name))

                    if self.include_pressure:
                        header.append('pressure')

                    controllers.append(bc)

                    pid += 1

            if controllers:
                self.data_manager = dm = CSVDataManager()
                ni = 'bakeout-{}'.format(generate_datestamp())
                self.data_name = dm.new_frame(directory='bakeouts',
                        base_frame_name=ni)
                d = map(str, map(int, [self.include_temp,
                        self.include_heat, self.include_pressure]))
                d[0] = '#' + d[0]
                self.data_manager.write_to_frame(d)

                # set the header in for the data file

                self.data_manager.write_to_frame(header)

                self._nactivated_controllers = len(controllers)

                for c in controllers:
                    c.run()
#                    time.sleep(0.5)

                if self.include_pressure:

                    # pressure plot

                    self.graph.new_series(type='line',
                            render_style='connectedpoints',
                            plotid=self.plotids[2])

                # start a pressure monitor thread
#                t = Thread(target=self._pressure_monitor)
#                t.start()

                self._start_time = time.time()

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
        for tr in self._get_controller_names():
            bc = self.trait_get(tr)[tr]
            bc.update_interval = self.update_interval

        self.graph.set_scan_delay(self.update_interval)

# ============= views ===================================

    def traits_view(self):
        '''
        '''
        controller_grp = HGroup()
        for tr in self._get_controller_names():
            controller_grp.content.append(Item(tr,
                                     show_label=False, style='custom'))

        control_grp = HGroup(VGroup(Item('execute',
                             editor=ButtonEditor(label_value='execute_label'
                             ), show_label=False,
                             enabled_when='execute_ok'),
                             Item('open_button',
                             editor=ButtonEditor(label_value='open_label'
                             ), show_label=False),
                            Item('edit_scripts_button', show_label=False,
                                 enabled_when='not alive'
                                 )
                                    ),
                             HGroup(Item('configuration',
                             editor=EnumEditor(name='configurations'),
                             show_label=False), Item('save',
                             show_label=False)),
                             VGroup('include_pressure', 'include_heat',
                             'include_temp', enabled_when='not alive'),
                             label='Control', show_border=True),

        scan_grp = VGroup(Item('update_interval',
                          label='Sample Period (s)'), Item('scan_window'
                          , label='Data Window (mins)'), label='Scan',
                          show_border=True)

        pressure_grp = VGroup(HGroup(Item('use_pressure_monitor'),
                              Item('_pressure_sampling_period',
                              label='Sample Period (s)')),
                              VGroup(Item('_max_duration',
                              label='Max. Duration (hrs)'),
                              Item('_pressure_monitor_std_threshold'),
                              Item('_pressure_monitor_threshold'),
                              enabled_when='use_pressure_monitor'),
                              label='Pressure', show_border=True)
        v = View(VGroup(HGroup(control_grp, HGroup(scan_grp,
                 pressure_grp, enabled_when='not alive')),
                 controller_grp, Item('graph', show_label=False,
                 style='custom')), handler=ManagerHandler,
                 resizable=True, title='Bakeout Manager', height=830)
        return v

    def _get_controller_names(self):
        '''
        '''

        c = [tr for tr in self.traits() if tr.startswith('bakeout')]
        c.sort()
        return c

    def _get_controllers(self):
        return [getattr(self, tr)
                for tr in self._get_controller_names()]

    def _get_active_controllers(self):
#        ac = []
#        for tr in self._get_controllers():
#            if tr.isActive() and tr.isAlive():
#                ac.append(tr)

        return [tr for tr in self._get_controllers() if tr.isActive()
                and tr.isAlive()
                ]

    def _load_configurations(self):
        '''
        '''

        self._configurations = ['---']
        for p in os.listdir(bakeout_config_dir):
            if os.path.splitext(p)[1] == '.cfg':
                self._configurations.append(os.path.join(bakeout_config_dir,
                        p))

    def _parse_config_file(self, p):
        config = self.get_configuration(p, warn=False)
        if config is None:
            return
        try:
            self.include_temp = config.getboolean('Include', 'temp')
            self.include_heat = config.getboolean('Include', 'heat')
            self.include_pressure = config.getboolean('Include',
                    'pressure')
        except NoSectionError:
            pass

        try:
            self.update_interval = config.getfloat('Scan', 'interval')
            self.scan_window = config.getfloat('Scan', 'window')
        except NoSectionError:
            pass

        for section in config.sections():
            if section.startswith('bakeout'):
                kw = dict()
                script = self.config_get(config, section, 'script',
                        optional=True)
                if script:
                    kw['script'] = script
                else:
                    kw['script'] = '---'
                    for opt in ['duration', 'setpoint']:
                        value = self.config_get(config, section, opt,
                                cast='float')
                        if value is not None:
                            kw[opt] = value

                    kw['record_process'] = self.config_get(config, section, 'record_process',
                                                           default=False,
                                                           optional=True,
                                                           cast='boolean'
                                                           )
                getattr(self, section).trait_set(**kw)

    def _get_configurations(self):
        return [os.path.basename(p) for p in self._configurations]

    def _get_configuration(self):
        return os.path.splitext(os.path.basename(self._configuration))[0]

    def _set_configuration(self, c):
        self._configuration = os.path.join(bakeout_config_dir, c)

    def _get_execute_label(self):
        return ('Stop' if self.alive else 'Execute')

    def __configuration_changed(self):
        for tr in self._get_controller_names():
            kw = dict()
            tr_obj = getattr(self, tr)
            for attr, v in [('duration', 0),
                             ('setpoint', 0),
                             ('record_process', False)]:
                kw[attr] = v

            kw['script'] = '---'
            tr_obj.trait_set(**kw)

        if self.configuration is not '---':
            self._parse_config_file(self._configuration)

    @on_trait_change('include_+')
    def toggle_graphs(self):
        self.graph = self._graph_factory()

    # ===========================================================================
    # graph manager interface
    # ===========================================================================

    def bakeout_factory(
        self,
        header,
        nseries,
        include_bits,
        data,
        path,
        ph=0.5,
        **kw
        ):

        ph = DISPLAYSIZE.height * ph / max(1, sum(include_bits))

        graph = self._graph_factory(stream=False,
                                    include_bits=include_bits,
                                    panel_height=ph,
                                    plot_kwargs=dict(pan=True, zoom=True),
                                     **kw)
        graph.redraw()
        plotids = self.plotids
        for i in range(nseries):

            # set up graph
            name = (header[(1 + sum(include_bits)) * i])[:-5]
            for j in range(3):
                if include_bits[j]:
                    graph.new_series(plotid=plotids[j])
                    graph.set_series_label(name, series=i,
                                           plotid=plotids[j])

#            if include_bits[1]:
#                graph.new_series(plotid=plotids[1])
#
#            if include_bits[2]:
#                graph.new_series(plotid=plotids[2])

#            for j in range(3):
#                if include_bits[j]:
#                    graph.set_series_label(name, series=i,
#                                           plotid=plotids[j])
#            elif include_bits[1]:
#                graph.set_series_label(name, series='bakeout{}'.format(i),
#                        plotid=plotids[1])

        for (i, da) in enumerate(data):
            da = np.transpose(da)
            x = da[0]
            if include_bits[0]:
                y = da[1]
                graph.set_data(x, series=i, axis=0, plotid=plotids[0])
                graph.set_data(da[1], series=i, axis=1,
                               plotid=plotids[0])
                graph.set_y_limits(min(y), max(y), pad='0.1',
                                   plotid=plotids[0])

            if include_bits[1]:
                y = da[2]
                graph.set_data(x, series=i, axis=0, plotid=plotids[1])
                graph.set_data(y, series=i, axis=1, plotid=plotids[1])
                graph.set_y_limits(min(y), max(y), pad='0.1',
                                   plotid=plotids[1])

            if include_bits[2]:
                y = da[3]
                graph.set_data(x, series=i, axis=0, plotid=plotids[2])
                graph.set_data(y, series=i, axis=1, plotid=plotids[2])
                graph.set_y_limits(min(y), max(y), pad='0.1',
                                   plotid=plotids[2])

                # prevent multiple pressure plots

                include_bits[2] = False

        graph.window_title = name = os.path.basename(path)
        graph.set_x_limits(min(x), max(x))
        (name, _ext) = os.path.splitext(name)
        graph.set_title(name)
        return graph

    def bakeout_parser(self, path):
        import csv
        with open(path, 'r') as f:
#            reader = csv.reader(open(path, 'r'))
            reader = csv.reader(f)

            # first line is the include bits
            l = reader.next()
            l[0] = (l[0])[1:]
#
            ib = map(int, l)

            # second line is a header
            header = reader.next()
            header[0] = (header[0])[1:]
            nseries = len(header) / (sum(ib) + 1)
            data = np.genfromtxt(f, delimiter=',',
                                 invalid_raise=False
                                 )
            data = np.array_split(data, nseries, axis=1)

        return (header, nseries, ib, data, path)

    # ------------------------------------------------------------------------------

    def _graph_factory(
        self,
        stream=True,
        graph=None,
        include_bits=None,
        panel_height=None,
        plot_kwargs=None,
        **kw
        ):

        if plot_kwargs is None:
            plot_kwargs = dict()

        if include_bits is None:
            include_bits = [self.include_temp, self.include_heat,
                            self.include_pressure]

        n = max(1, sum(map(int, include_bits)))
        if graph is None:

            if stream:
                graph = TimeSeriesStreamStackedGraph(panel_height=435 / n,
                                    container_dict=dict(padding_top=30),
                         **kw)
            else:
                if panel_height is None:
                    panel_height = DISPLAYSIZE.height * 0.65 / n

                graph = \
                    TimeSeriesStackedGraph(panel_height=panel_height, **kw)

        graph.clear()
        kw['data_limit'] = self.scan_window * 60 / self.update_interval
        kw['scan_delay'] = self.update_interval

        self.plotids = [0, 1, 2]

        # temps

        if include_bits[0]:
            graph.new_plot(show_legend='ll', **kw)
            graph.set_y_title('Temp (C)')
        else:
            self.plotids = [0, 0, 1]

        # heat power

        if include_bits[1]:
            graph.new_plot(**kw)
            graph.set_y_title('Heat Power (%)', plotid=self.plotids[1])
        elif not include_bits[0]:
            self.plotids = [0, 0, 0]
        else:
            self.plotids = [0, 0, 1]

        # pressure

        if include_bits[2]:
            graph.new_plot(**kw)
            graph.set_y_title('Pressure (torr)', plotid=self.plotids[2])

        if include_bits:
            graph.set_x_title('Time')
            graph.set_x_limits(0, self.scan_window * 60)

        return graph

    def _graph_default(self):
        g = self._graph_factory()
        return g


def launch_bakeout():
    b = BakeoutManager()
    b.load()
    b.load_controllers()

    b.configure_traits()


# ============= EOF ====================================
