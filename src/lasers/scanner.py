#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Instance, List, Bool, Button, Event, String, \
    Property, Float, Str, Tuple, File, Any, Int
from traitsui.api import View, Item, Controller, UItem, ButtonEditor
from pyface.timer.do_later import do_after
#============= standard library imports ========================
import time
#============= local library imports  ==========================
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.graph.stream_graph import StreamStackedGraph
from src.helpers.timer import Timer
from src.loggable import Loggable
from threading import Thread
import os
import yaml
from src.application_controller import ApplicationController
from src.lasers.laser_managers.ilaser_manager import ILaserManager


class ScannerController(ApplicationController):
    execute_button = Event
    execute_label = Property(depends_on='model._scanning')

    def traits_view(self):
        v = View(UItem('controller.execute_button',
                       editor=ButtonEditor(label_value='controller.execute_label')
                       ),
                 Item('setpoint', enabled_when='_scanning'),
                 )
        return v

    def controller_execute_button_changed(self, info):
        if self.model.execute():
            self.open_view(self.model.graph)

    def _get_execute_label(self):
        return 'Stop' if self.model._scanning else 'Start'

class Scanner(Loggable):
    '''
        Scanner is a base class for display a scan of device data
        
        ScanableDevices has this ability built in but more complicated scans are
        best done here. ScanableDevice scan is best used from continuous long term recording 
        of a single or multiple values
    '''

    graph = Instance(StreamStackedGraph)
    manager = Instance(ILaserManager)

    data_manager = Instance(CSVDataManager, ())
    '''
        list of callables. should return a signal value for graphing
    '''
    functions = List
    static_values = List

    scan_period = Int  # ms
    stop_event = Event
    setpoint = Float(enter_set=True, auto_set=False)
    control_path = File

    _warned = False
    _scanning = Bool

    def new_static_value(self, name, *args, **kw):
        self.static_values.append((name, None))
        if args:
            self.set_static_value(name, *args, **kw)

    def set_static_value(self, name_or_idx, value, plotid=None):
        '''
            if the plotid is not None add a horizontal guide at value
        '''
        if isinstance(name_or_idx, str):
            name_or_idx = next((i for i, (e, a) in enumerate(self.static_values)), None)

        if name_or_idx is not None:
            name = self.static_values[name_or_idx][0]
            self.static_values[name_or_idx] = (name, value)

        if plotid is not None:
            self.graph.add_horizontal_rule(value, plotid=plotid)

    def setup(self, directory=None, base_frame_name=None):
        self.data_manager.new_frame(directory=directory,
                                    base_frame_name=base_frame_name)

    def new_function(self, function, name=None):
        if name is None:
            name = function.func_name

        g = self.graph
        func = self.functions
        kw = dict(ytitle=name,)
        n = len(func)
        if n == 0:
            kw['xtitle'] = 'Time'

        g.new_plot(
                   data_limit=1000,
                   **kw)
        g.new_series(plotid=n)

        self.functions.append((function, name))


    def stop(self):
        self._timer.Stop()
        self._scanning = False
        self.stop_event = True
        self.info('scan stopped')
        if self.manager:
            self.manager.disable_device()

    def execute(self):

        if self._scanning:
            self.stop()
        else:
            # write metadata if available
            self._write_metadata()

            # make header row
            header = ['t'] + \
                        self._make_func_names() + \
                            [n for n, _ in self.static_values]
            self.data_manager.write_to_frame(header)

            self._starttime = time.time()
            yd = self._read_control_path()
            if yd is None:
                sp = 1000
            else:
                sp = yd['period']

            if self.manager.enable_device():

                # starts automatically
                self._timer = Timer(sp, self._scan)

                self.info('scan started')
                self._scanning = True
    #            yd = self._read_control_path()
                if yd is not None:
                    # start a control thread
                    self._control_thread = Thread(target=self._control,
                                                  args=(yd,)
                                                  )
                    self._control_thread.start()
                    self.info('control started')
            else:
                self.info('no manager available')

        return self._scanning

    def _control(self, ydict):
        self.start_control_hook()

        start_delay = ydict['start_delay']
        end_delay = ydict['end_delay']
        setpoints = ydict['setpoints']

        self.set_static_value('Setpoint', 0)
        time.sleep(start_delay)
        for t, d in setpoints:
            if self._scanning:
                self.setpoint = t

                if self.manager:
                    self.manager.set_laser_temperature(t)

                self.set_static_value('Setpoint', t, plotid=0)
                self.info('setting setpoint to {} for {}s'.format(t, d))
                st = time.time()
                while time.time() - st < d and self._scanning:
                    time.sleep(1)

        if self._scanning:
            self.setpoint = 0
            self.set_static_value('Setpoint', 0)
            time.sleep(end_delay)
            self.stop()

        self.end_control_hook(self._scanning)

    def start_control_hook(self):
        pass
    def end_control_hook(self, ok):
        pass

    def _make_func_names(self):
        return [name for _, name in self.functions]

    def _write_metadata(self):
        pass

    def _scan(self):
        functions = self.functions
        data = []
        record = self.graph.record

        x = time.time() - self._starttime
        for i, (func, _) in enumerate(functions):
            try:
                if hasattr(func, 'next'):
                    func = func.next

                v = float(func())
                data.append(v)

                # do_after no longer necessary with Qt
                record(v, plotid=i, x=x, do_after=None)
            except Exception, e:
                print e

        sv = []
        for _, v in self.static_values:
            if v is None:
                v = ''
            sv.append(v)

        data = [x] + data + sv
        self.data_manager.write_to_frame(data)

    def _read_control_path(self):
        if os.path.isfile(self.control_path):
            self._warned = False
            return yaml.load(open(self.control_path).read())
        elif not self._warned:

            self.warning_dialog('Not Scanner Control file found at {}'.format(self.control_path))
            self._warned = True
#===============================================================================
# defaults
#===============================================================================
    def _graph_default(self):
        g = StreamStackedGraph(window_x=50,
                               window_y=100)

        return g

class PIDScanner(Scanner):
    pid = Tuple
    def _write_metadata(self):
        if self.control_path:
            yd = self._read_control_path()
            if yd:
                self.pid = tuple(yd['pid'])
                pid = ['pid= {}, {}, {}'.format(*self.pid)]
                self.data_manager.write_to_frame(pid)

    def start_control_hook(self):
        if self.manager:
            tc = self.manager.temperature_controller

            if tc:

                p, i, d = self.pid
                tc.set_time_integral(i)
                tc.set_time_derivative(d)
            else:
                self.debug('no manager temperature controol available')

        else:
            self.debug('no manager available')
#    def _control_path_changed(self):

if __name__ == '__main__':
    import random
    def random_generator(scale=1):
        def random_gen():
            return random.random() * scale

        f = random_gen
        f.func_name = 'RScale{}'.format(scale)
        return random_gen

    def generator():
        def gen():
            while 1:
                for i in (1, 100):
                    yield random.random() * i
        return gen

    gen = generator()

    s = Scanner()
#    s.new_function(random_generator(), ytitle='random', directory='random_scan')
#    s.new_function(random_generator(scale=10), ytitle='random', directory='random_scan')
    gg = gen()
    s.new_function(gg, name='random1', directory='random_scan')
    s.new_function(gg, name='random2', directory='random_scan')
    s.new_static_value('Setpoint', 10, plotid=1)
    sc = ScannerController(model=s)
    sc.configure_traits()
#============= EOF =============================================
