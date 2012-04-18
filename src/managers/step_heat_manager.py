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
from traits.api import Instance, Any, Float, Bool, Property, Event
from traitsui.api import View, Item, HGroup, VGroup

#============= standard library imports ========================
import time
import os

#============= local library imports  ==========================
from src.graph.graph import Graph
from src.managers.manager import Manager
from threading import Thread
from src.experiment.heat_schedule import HeatSchedule
from src.helpers.paths import data_dir
from src.graph.time_series_graph import TimeSeriesStreamGraph
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.managers.videoable import Videoable
from src.helpers.filetools import unique_dir
import random
from src.managers.video_manager import VideoManager

class StepHeatManager(Manager, Videoable):
    graph = Instance(Graph)

    heat_event = Event
    heat_label = Property(depends_on='heating')
    heating = Bool
    laser_manager = Any
    data_manager = Instance(CSVDataManager, ())

    heat_schedule = Instance(HeatSchedule, ())

    sample_period = Float(1)
    def _heat_(self):
        self.graph = self._graph_factory()
        manager = self.laser_manager
        hs = self.heat_schedule
        hs.reset_steps()

        '''
            alogrithm
            
            
            set power
            wait duration
            while waiting take measurements for time vs power graph
            after duration elapsed take measurement for rpower vs power
            
        '''
        dm = self.data_manager
        root = os.path.join(data_dir, 'step_heats')
        root = unique_dir(root, 'stepheat')


        tvt = dm.new_frame(path=os.path.join(root, 'time_vs_temp.csv'))
        rvt = dm.new_frame(path=os.path.join(root, 'request_vs_actual.csv'))
        dm.write_to_frame(('Time', 'TC Temp', 'Py Temp'), frame_key=tvt)
        dm.write_to_frame(('Request', 'TC Temp', 'Py Temp'), frame_key=rvt)

        record_video = False
        if record_video:
            if self.video_manager is not None:
                self.video_manager.start_recording(os.path.join(root, 'video.avi'))


        manager.enable_laser()
        manager.set_zoom(25, block=True)
        manager.set_light(False)
        self.graph.set_time_zero()
        cnt = 1
        prevtime = 0
        ti = 0


        temps = [hi.temp_or_power for hi in hs.steps]

        self.graph.set_x_limits(min=min(temps),
                                max=max(temps),
                                pad=5, plotid=1)

        for i, hi in enumerate(hs.steps):
            if not self.isAlive():
                break

            dev = 0
            self.heat_schedule.current_step = hi

            tvti = dm.new_frame(path=os.path.join(root, 'time_vs_temp_{:02n}.csv'.format(i)))
            duration = hi.duration
            tp = hi.temp_or_power
            self.info('executing heat step {} {}={} duration={}'.format(i, 'temp', tp, duration))

            hi.state = 'running'

            #set power
            manager.set_laser_power(tp)
            while ti <= hi.duration * (i + 1):
                hi.elapsed_time = ti - prevtime + self.sample_period
                if not self.isAlive():
                    break

                time.sleep(max(0, self.sample_period - dev))

                #mjtc = manager.get_process_temperature()
                mjtc = 300
                mjpy = manager.get_pyrometer_temperature()

                ti = self.graph.record_multiple((mjtc, mjpy), do_after=1)

                dev = ti - self.sample_period * cnt
                cnt += 1

                dm.write_to_frame((ti, mjtc, mjpy), frame_key=tvt)

                #write individual steps
                dm.write_to_frame((ti, mjtc, mjpy), frame_key=tvti)

            prevtime = ti
            if not self.isAlive():
                break

            self.graph.add_vertical_rule(ti)

            self.graph.add_datum((tp, mjtc), plotid=1, do_after=1)
            self.graph.add_datum((tp, mjpy), plotid=1, series=1, do_after=1)
            dm.write_to_frame((tp, mjtc, mjpy), frame_key=rvt)

            if self.video_manager is not None:
                self.video_manager.snapshot(root=root)

            if self.isAlive():
                hi.state = 'success'
            else:
                hi.state = 'fail'

        if record_video and self.isAlive():
            self.video_manager.stop_recording()

        if self.isAlive():
            self.heating = False
            self.info('Step heat finished')

    def isAlive(self):
        return self.heating

    def _heat_event_fired(self):
        if not self.heating:
            self.info('start heating')
            t = Thread(target=self._heat_)
            self.heating = True
            t.start()
        else:
            self.heating = False
            self.info('heating canceled by user')

    def _heating_changed(self):
        if not self.heating:
            self.laser_manager.disable_laser()

    def _get_heat_label(self):
        return 'Start' if not self.heating else 'Stop'

    def _graph_factory(self):
        g = TimeSeriesStreamGraph()
        g.new_plot(xtitle='Time',
                   ytitle='Temp C',
                   link=False,
                   data_limit=300,
                   scan_delay=self.sample_period,
                   padding_top=10,
                   padding_left=20,
                   padding_right=10
                   )

        g.new_series()
        g.new_series()
        g.new_plot(xtitle='Request Temp C',
                   ytitle='Temp C',
                   link=False,
                   data_limit=50,
                   padding_top=10,
                   padding_left=20,
                   padding_right=10
                   )

        g.new_series(plotid=1, time_series=False)
        g.new_series(plotid=1, time_series=False)
        return g

    def _graph_default(self):
        return self._graph_factory()

    def _video_manager_default(self):
        return VideoManager()

    def traits_view(self):
        #if not self.simulation:
        self.video_manager.start(user='shm_underlay')
        self.video_manager.canvas.show_grids = False
        self.video_manager.width = 640
        self.video_manager.height = 480
        video = Item('video_manager', width=0.65, show_label=False, style='custom')

        graph = Item('graph', height=0.65, show_label=False, style='custom')
        v = View(
                 VGroup(
                        self._button_factory('heat_event', 'heat_label', None, align='right'),

                        HGroup(
                               video,
                               VGroup(
                                      graph,
                                      Item('heat_schedule', height=0.35, show_label=False, style='custom'),
                                     )
                               ),
                        ),

               resizable=True,
               width=1250,
               height=650,
               title='Step Heat Manager',
               handler=self.handler_klass
               )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup

    logging_setup('stepheater')
    class DummyManager(object):
        def set_laser_power(self, *args):
            pass
        def get_process_temperature(self):
            return random.random()
        def get_pyrometer_temperature(self):
            return random.random()
        def enable_laser(self):
            pass
        def disable_laser(self):
            pass
        def set_zoom(self, *args, **kw):
            pass

    s = StepHeatManager(laser_manager=DummyManager(),
                        simulation=True)

    s.configure_traits()
#============= EOF =============================================
