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
from traitsui.api import View, Item, HGroup, HSplit, VGroup, spring, \
    ButtonEditor, EnumEditor, ListEditor
from pyface.timer.api import do_after as do_after_timer

import numpy as np
import os
import time
from threading import Thread, Lock

from src.managers.manager import Manager, ManagerHandler
from src.hardware.bakeout_controller import BakeoutController
from src.hardware.core.communicators.rs485_scheduler import RS485Scheduler
from src.helpers.paths import bakeout_config_dir, data_dir, scripts_dir
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
from src.managers.data_managers.data_manager import DataManager
from src.helpers.archiver import Archiver
from src.managers.data_managers.h5_data_manager import H5DataManager

BATCH_SET_BAUDRATE = False
BAUDRATE = '38400'

from wx import GetDisplaySize
DISPLAYSIZE = GetDisplaySize()

class BakeoutParameters(HasTraits):
    setpoint = Float
    duration = Float
    max_output = Float
    script = Str
    name = Str
    script_text = Str
    view = View(
               Item('duration', style='readonly'),
               Item('setpoint', style='readonly'),
               Item('max_output', style='readonly'),
               Item('script', style='readonly'),
               Item('script_text', show_label=False, style='custom',
                    enabled_when='0')
                               )


class BakeoutGraphViewer(HasTraits):
    graph = Instance(Graph)
    bakeouts = List
    title = Str
    window_x = Float
    window_y = Float
    window_width = Float
    window_height = Float
    def new_controller(self, name):
        bc = BakeoutParameters(name=name)
        self.bakeouts.append(bc)
        return bc

    def traits_view(self):
        bakeout_group = Item('bakeouts', style='custom',
                             show_label=False,
                             editor=ListEditor(use_notebook=True,
                                                           dock_style='tab',
                                                           page_name='.name'
                                                           ))
        v = View(HSplit(Item('graph', style='custom', show_label=False),
                        bakeout_group
                        ),
                 resizable=True,
                 title=self.title,
                 x=self.window_x,
                 y=self.window_y,
                 width=self.window_width,
                 height=self.window_height
                 )
        return v


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
    data_manager = Instance(DataManager)

#    def _convert_to_h5(self, path):
#        args = self._bakeout_csv_parser(path)
#        (names, nseries, ib, data, path, attrs) = args
#        dm = H5DataManager()
#        dm.new_frame()
#        for n, d in zip(names, data):
#            g = dm.new_group(n)
#            print d.transpose()
#            dm.new_array('/{}'.format(n), 'data', d.transpose())
#
#        dm.close()

#===============================================================================
# Button handlers
#===============================================================================
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
                                  'bakeouts'),
                                  wildcard='Data files (*.h5,*.csv, *.txt)|*.h5;*.csv;*.txt'
                                  )
        if path is not None:
            self._open_graph(path)

    def _save_fired(self):

        path = self._file_dialog_('save as',
                                  default_directory=bakeout_config_dir)

        if not path.endswith('.cfg'):
            path += '.cfg'

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
        if self.alive:
            self.alive = False
            self.kill(user_kill=True)
        else:
            self.alive = True
            t = Thread(target=self._execute_)
            t.start()

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

        self._load_controllers()

    def update_alive(
        self,
        obj,
        name,
        old,
        new,
        ):
        if new:
            self.alive = new
        else:
            self.alive = bool(len(self._get_active_controllers()))

    def kill(self, **kw):
        '''
        '''
        if self.data_manager is not None:
            self.data_manager.close()

        self._clean_archive()

        if 'user_kill' in kw:
            if not kw['user_kill']:
                super(BakeoutManager, self).kill()
        else:
            super(BakeoutManager, self).kill()

        for tr in self._get_controller_names():
            getattr(self, tr).end(**kw)

    def _execute_(self):
        '''
        '''
        self._buffer_lock = Lock()
        pid = 0
        header = []
        self.data_buffer = []
        self.data_buffer_x = []
        self.data_count_flag = 0
        self.graph_info = dict()
        self.graph = self._graph_factory()

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
            self.data_manager = self._data_manager_factory(controllers, header,
                                                           style='h5')

            self._nactivated_controllers = len(controllers)

            for c in controllers:
                c.run()

            time.sleep(0.01)
            for c in controllers:
                c.start_timer()

            if self.include_pressure:

                # pressure plot

                self.graph.new_series(type='line',
                        render_style='connectedpoints',
                        plotid=self.plotids[2])

            # start a pressure monitor thread
#                t = Thread(target=self._pressure_monitor)
#                t.start()

            self._start_time = time.time()
        else:
            self.alive = False

    def _graph_(self):
        for ci, (_name, i, pi, hi) in enumerate(self.data_buffer):
            track_x = ci == len(self.data_buffer) - 1
            kwargs = dict(series=i,
                        track_x=track_x,
                        track_y=False,
#                        do_later=10
                        )

            if self.include_temp:
                kwargs['plotid'] = self.plotids[0]
                nx = self.graph.record(pi, **kwargs)

            if self.include_heat:
                kwargs['plotid'] = self.plotids[1]
                kwargs['x'] = nx
                kwargs['track_x'] = False if self.include_temp else track_x
                self.graph.record(hi, **kwargs)

            self.data_buffer_x.append(nx)

        try:
            self.graph.update_y_limits(plotid=self.plotids[0]
                                       #, force=False
                                       )
        except IndexError:
            pass
        try:
            self.graph.update_y_limits(plotid=self.plotids[1]
                                       #, force=False
                                       )
        except IndexError:
            pass

        if self.include_pressure:
            self._get_pressure(nx)

#        self._write_data()

        self.data_buffer = []
        self.data_buffer_x = []
        self.data_count_flag = 0

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
                                 ),
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

    def _load_controllers(self):
        '''
        '''

        scheduler = RS485Scheduler()
        program = False
        cnt = 0
        for bc in self._get_controllers():
            # set the communicators scheduler
            # used to synchronize access to port
            if bc.load():
                bc.set_scheduler(scheduler)

                if bc.open():
                    '''
                        on first controller check to see if
                        memory block programming is required

                        if it is apply to all subsequent controllers
                    '''
                    if cnt == 0:
                        if not bc.is_programmed():
                            program = True
                        m1 = 'Watlow controllers require programming. Programming automatically'
                        m2 = 'Watlow controllers are properly programmed'
                        self.info(m1 if program else m2)

                    bc.program_memory_blocks = program

                    bc.initialize()
                    cnt += 1

#                    if BATCH_SET_BAUDRATE:
#                        bc.set_baudrate(BAUDRATE)

        self._load_configurations()
        return True

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

                    kw['record_process'] = self.config_get(config, section,
                                                           'record_process',
                                                           default=False,
                                                           optional=True,
                                                           cast='boolean'
                                                           )
                getattr(self, section).trait_set(**kw)

    def _open_graph(self, path):
        ish5 = True if path.endswith('.h5') else False

        args = self._bakeout_parser(path, ish5)
        if args is None:
            return
        names = args[0]
        attrs = args[-1]
        graph = self._bakeout_factory(ph=0.65,
                *args,
                container_dict=dict(
                                    #bgcolor='red',
                                    #fill_bg=True,
                                    padding_top=60
                                    ),
                transpose_data=not ish5
                )

        if ish5:
            b = BakeoutGraphViewer(graph=graph,
                                   title=path,
                                   window_x=30,
                                   window_y=30,
                                   window_width=0.66,
                                   window_height=0.85
                                   )
            for name, ais in zip(names, attrs):
                bc = b.new_controller(name)
                for key, value in ais.iteritems():
                    setattr(bc, key, value)

            b.edit_traits()

        else:
            graph.window_title = name = os.path.basename(path)
            graph.window_width = 0.66
            graph.window_height = 0.85
            graph.window_x = 30
            graph.window_y = 30
            graph.edit_traits()

#==============================================================================
#     trait change handlers
#==============================================================================
#    def _get_process_value(self):
#        while 1:
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
                self.data_buffer.append((obj.name, pid, pv, hp))

                self.data_count_flag += 1

                if self.data_count_flag >= len(self.active_controllers):
                    self._write_data()
                    do_after_timer(1, self._graph_)

    def _update_interval_changed(self):
        for tr in self._get_controller_names():
            bc = self.trait_get(tr)[tr]
            bc.update_interval = self.update_interval

        self.graph.set_scan_delay(self.update_interval)

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
    def _toggle_graphs(self):
        self.graph = self._graph_factory()

    def _clean_archive(self):
        root = os.path.join(data_dir, 'bakeouts')
        self.info('cleaning bakeout data directory {}'.format(root))
        a = Archiver(root=root, archive_days=14)
        a.clean()

# ==========================================================================
# factories
# ==========================================================================
    def _controller_factory(self, name):
        bc = BakeoutController(name=name,
                               configuration_dir_name='bakeout',
                               update_interval=self.update_interval)
        return bc

    def _data_manager_factory(self, controllers, header, style='csv'):
        from src.managers.data_managers.h5_data_manager import H5DataManager

        dm = CSVDataManager() if style == 'csv' else H5DataManager()

        ni = 'bakeout-{}'.format(generate_datestamp())
        _dn = dm.new_frame(directory='bakeouts',
                base_frame_name=ni)

        if style == 'csv':
            d = map(str, map(int, [self.include_temp,
                    self.include_heat, self.include_pressure]))
            d[0] = '#' + d[0]
            dm.write_to_frame(d)

            # set the header in for the data file
            dm.write_to_frame(header)
        else:
            for ci in controllers:
                cgrp = dm.new_group(ci.name)
                if self.include_temp:
                    dm.new_table(cgrp, 'temp')
                if self.include_heat:
                    dm.new_table(cgrp, 'heat')
                if self.include_pressure:
                    dm.new_table(cgrp, 'pressure')

                for attr in ['script', 'setpoint',
                             'duration', 'max_output']:
                    dm.set_group_attribute(cgrp, attr, getattr(ci, attr))

                if ci.script != '---':
                    p = os.path.join(scripts_dir, 'bakeoutscripts', ci.script)
                    with open(p, 'r') as f:
                        txt = f.read()
                else:
                    txt = ''
                dm.set_group_attribute(cgrp, 'script_text', txt)
        return dm

    def _bakeout_factory(
        self,
#        header,
        names,
        nseries,
        include_bits,
        data,
        path,
        attrs,
        ph=0.5,
        transpose_data=True,
        ** kw
        ):

        ph = DISPLAYSIZE.height * ph / max(1, sum(include_bits))

        graph = self._graph_factory(stream=False,
                                    include_bits=include_bits,
                                    panel_height=ph,
                                    plot_kwargs=dict(pan=True, zoom=True),
                                     **kw)
        plotids = self.plotids
#        print names, nseries, include_bits
#        for i in range(nseries / sum(include_bits)):
#            print i
            # set up graph
#            name = names[i]#[i / sum(include_bits)]
        for i, name in enumerate(names):
            for j in range(3):
                if include_bits[j]:
                    graph.new_series(plotid=plotids[j])
                    graph.set_series_label(name, series=i,
                                           plotid=plotids[j])

        ma0 = -1
        mi0 = 1e8
        ma1 = -1
        mi1 = 1e8
        ma2 = -1
        mi2 = 1e8

        for (i, da) in enumerate(data):

            if transpose_data:
                da = np.transpose(da)

            x = da[0]
            if include_bits[0]:
                y = da[1]
                ma0 = max(ma0, max(y))
                mi0 = min(mi0, min(y))
                graph.set_data(x, series=i, axis=0, plotid=plotids[0])
                graph.set_data(da[1], series=i, axis=1,
                               plotid=plotids[0])
                graph.set_y_limits(mi0, ma0, pad='0.1',
                                   plotid=plotids[0])

            if include_bits[1]:
                y = da[2]
                ma1 = max(ma1, max(y))
                mi1 = min(mi1, min(y))
                graph.set_data(x, series=i, axis=0, plotid=plotids[1])
                graph.set_data(y, series=i, axis=1, plotid=plotids[1])
                graph.set_y_limits(mi1, ma1, pad='0.1',
                                   plotid=plotids[1])

            if include_bits[2]:
                y = da[3]
                ma2 = max(ma2, max(y))
                mi2 = min(mi2, min(y))
                graph.set_data(x, series=i, axis=0, plotid=plotids[2])
                graph.set_data(y, series=i, axis=1, plotid=plotids[2])
                graph.set_y_limits(mi2, ma2, pad='0.1',
                                   plotid=plotids[2])

                # prevent multiple pressure plots

                include_bits[2] = False

        graph.set_x_limits(min(x), max(x))
        (name, _ext) = os.path.splitext(name)
        graph.set_title(name)
        return graph

    def _bakeout_parser(self, path, ish5):

        if ish5:
            return self._bakeout_h5_parser(path)
        else:
            return self._bakeout_csv_parser(path)

    def _write_data(self):

        if isinstance(self.data_manager, CSVDataManager):
            self._write_csv_data()
        else:
            self._write_h5_data()
#        for i in range(100):
#            self._write_csv_data()
#            self._write_h5_data()

    def _write_h5_data(self):
        dm = self.data_manager
        for ((name, _, pi, hp), xi) in zip(self.data_buffer,
                                             self.data_buffer_x):
            for (ti, di, inc) in [('temp', pi, self.include_temp),
                                  ('heat', hp, self.include_heat),
                                  ]:
                if inc:
                    table = dm.get_table(ti, name)
                    if table is not None:
                        row = table.row
                        row['time'] = xi
                        row['value'] = di
                        row.append()
                        table.flush()

    def _write_csv_data(self):
        ns = sum(map(int, [self.include_heat,
                           self.include_pressure, self.include_temp])) + 1
        container = [0, ] * ns * self._nactivated_controllers

        for (sub, x) in zip(self.data_buffer, self.data_buffer_x):
            s = 1
            (_, pid, pi, hp) = sub

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

        self.data_manager2.write_to_frame(container)

    def _bakeout_h5_parser(self, path):
        from src.managers.data_managers.h5_data_manager import H5DataManager
        dm = H5DataManager()
        if not dm.open_data(path):
            return

        controllers = dm.get_groups()
        datagrps = []
        attrs = []
        ib = [0, 0, 0]
        for ci in controllers:

            attrs_i = dict()
            for ai in ['script', 'setpoint', 'duration', 'script_text']:
                attrs_i[ai] = getattr(ci._v_attrs, ai)
            attrs.append(attrs_i)
            data = []
            for i, ti in enumerate(['temp', 'heat']):
                try:
                    table = getattr(ci, ti)
                    xs = [x['time'] for x in table]
                    ys = [x['value'] for x in table]
                    if i == 0:
                        data.append(xs)
                    data.append(ys)
                    ib[i] = 1
                except Exception, e:
                    print 'bakeout_manager._bakeout_h5_parser', e

            if data:
                datagrps.append(data)

        names = [ci._v_name for ci in controllers]
        nseries = len(controllers) * sum(ib)
        return names, nseries, ib, np.array(datagrps), path, attrs

    def _bakeout_csv_parser(self, path):
        import csv
        attrs = None
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
            names = [(header[(1 + sum(ib)) * i])[:-5] for i in range(nseries)]

#            average load time for 2MB file =0.42 s (n=10)
#            data = np.loadtxt(f, delimiter=',')

#            average load time for 2MB file = 0.19 s (n=10)
            data = np.array([r for r in reader], dtype=float)

            data = np.array_split(data, nseries, axis=1)
        return (names, nseries, ib, data, path, attrs)

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

    def _script_editor_default(self):
        m = ScriptManager(kind='Bakeout',
                          default_directory_name='bakeoutscripts')
        return m

    def _get_configurations(self):
        return [os.path.basename(p) for p in self._configurations]

    def _get_configuration(self):
        return os.path.splitext(os.path.basename(self._configuration))[0]

    def _set_configuration(self, c):
        self._configuration = os.path.join(bakeout_config_dir, c)

    def _get_execute_label(self):
        return 'Stop' if self.alive else 'Execute'

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

    def _get_execute_ok(self):
        return sum(map(int, [self.include_temp, self.include_heat,
                   self.include_pressure])) > 0

#==============================================================================
# Pressure
#==============================================================================
    def _get_pressure(self, x):
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
#            self.graph.record(nv, track_y=(5e-3, None), track_y_pad=5e-3, 
#                    track_x=False, plotid=2, do_later=10)
#
#            if self.use_pressure_monitor:
#                dbuffer = np.hstack((dbuffer[-window:], nv))
#                n = len(dbuffer)
#                std = dbuffer.std()
#                mean = dbuffer.mean()
#                if std < self._pressure_monitor_std_threshold:
#                    if mean < self._pressure_monitor_threshold:
#                        self.info('pressure set point achieved:mean={} std={}
#                                     n={}'.format(mean, std, n))
#                        success = True
#                        break
#
#            time.sleep(self._pressure_sampling_period)
#            if not self.isAlive():
#                break
#
#        for ac in self._get_active_controllers():
#            ac.end(error=None if success else 'Max duration exceeded max={:0.1f}, dur={:0.1f}'.format(self._max_duration,

def launch_bakeout():
    b = BakeoutManager()
    b.load()
    b.configure_traits()

##bm = BakeoutManager()
#
#
#def load_h5():
#    bm._bakeout_h5_parser(path + '.h5')
#
#
#def load_csv():
#    bm._bakeout_csv_parser(path + '.txt')
#
if __name__ == '__main__':
    path = os.path.join(data_dir, 'bakeouts', 'bakeout-2012-03-31007.txt')
    b = BakeoutManager()
#    b._convert_to_h5(path)
#    n = 10
#    from timeit import Timer
#    t = Timer('load_h5()', 'from __main__ import load_h5')
#    h5_time = t.timeit(n) / float(n)
#    print 'h5', h5_time
#
#    t = Timer('load_csv()', 'from __main__ import load_csv')
#    csv_time = t.timeit(n) / float(n)
#
#    print 'csv', csv_time
# ============= EOF ====================================
