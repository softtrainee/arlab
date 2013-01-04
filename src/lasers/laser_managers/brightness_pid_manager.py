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

#============= enthought library imports =======================
from traits.api import Instance, Float, Bool, Any, DelegatesTo
from traitsui.api import View, Item, HGroup, Spring, RangeEditor
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
import random
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.hardware.core.pid_object import PIDObject
from src.paths import paths
#from src.helpers.timer import Timer
from pyface.timer.api import Timer
from src.graph.stream_graph import StreamGraph
from src.machine_vision.brigthness_manager import BrightnessManager
#from pyface.timer.api import do_later


from traits.api import HasTraits, Button, Str
from threading import Thread
class DummySM(HasTraits):
    video = Any
    _camera_xcoefficients = '1, 231'
    def _video_default(self):
        from src.image.video import Video
        v = Video()
        v.open(identifier=1)
        return v

class DummyParent(HasTraits):

    enabled = Bool(True)
    enable = Button
    enable_label = Str

    request_power = Float
    application = Any
    stage_manager = DummySM()
    zoom = 0
    def _enable_fired(self):
        self.enabled = not self.enabled

    def set_laser_power(self, p, **kw):
        self.request_power = p


class PID:
    _integral_err = 0
    _prev_err = 0
    Kp = 0.25
    Ki = 0.0001
    Kd = 0
    def get_value(self, error, dt):
        self._integral_err += (error * dt)
        derivative = (error - self._prev_err) / dt
        output = (self.Kp * error) + (self.Ki * self._integral_err) + (self.Kd * derivative)
        self._prev_err = error
        return output

PDD = PID()

class BrightnessPIDManager(Manager):
    pid_object = Instance(PIDObject)
    brightness_timer = None
    pid_loop_period = 750
    setpoint = Float(auto_set=False, enter_set=True)
    output = Float
    error = Float
    graph = Instance(StreamGraph)
    brightness_manager = Instance(BrightnessManager)
    _collect_baseline = Bool(True)
    _collect_baseline = Bool(False)

    request_power = DelegatesTo('parent')

    enabled = DelegatesTo('parent')
    enable = DelegatesTo('parent')
    enable_label = DelegatesTo('parent')

    application = DelegatesTo('parent')

#    cnt = 0
#    slope = 1
#    _prev_v = 0
#    _reset_cnt = True
    def set_brightness_setpoint(self, b):
        #start a timer for the pid loop
        self.info('setting brightness {}'.format(b))
        #stop the timer if its already running
        if self.brightness_timer:
            self.brightness_timer.Stop()

        if b:
            self.brightness_timer = Timer(self.pid_loop_period, self.set_output, b)

#    def get_value(self):
#        if self.output > 0:
#            m = 0.25 * self.output
#            v = m * self.cnt + self._prev_v
#            self._prev_v = v
#            self._reset_cnt = True
#        else:
#            if self._reset_cnt:
#                self._reset_cnt = False
#                self.cnt = 0
#            v = -0.05 * self.cnt + self._prev_v
#        print self.output, v
#        self.cnt += 1

#        if self.brightness_manager:
#            v = self.brightness_manager.get_value(verbose=False)
#            

#        return v

    def set_output(self, sp):
        #get the current brightness error
        brightness = self.brightness_manager.get_value(verbose=False)
        err = sp - brightness

        #get the pid output
        out = self.pid_object.get_value(err)

        if self.parent:
            self.parent.set_laser_power(out,
                                        verbose=False,
#                                        memoize_calibration=True
                                        )

        self.output = out
        self.error = err
        self.graph.record_multiple((err, out, brightness), do_after=10)

    def close(self, is_ok):
        self._dump_pid_object()
        if self.brightness_timer:
            self.brightness_timer.Stop()

#        if self.brightness_manager:
#            self.brightness_manager.close_images()

        return True

    def traits_view(self):
        ctrl_grp = HGroup(
                        self._button_factory('enable', 'enable_label'),
                        Item('request_power', editor=RangeEditor(low=0,
                                                          high=100),
                             enabled_when='object.enabled',
                             show_label=False,
                             width=0.8
                             ),
                        )
        v = View(
                 ctrl_grp,
                 Item('pid_object', style='custom', show_label=False),
                 Item('setpoint', enabled_when='object.enabled'),
                 HGroup(Item('output', style='readonly', format_str='%0.3f'),
                        Spring(width=60, springy=False),
                         Item('error', style='readonly', format_str='%0.3f')),
                 Item('graph', show_label=False, style='custom'),
                 handler=self.handler_klass(),
                 resizable=True,
                 title='Configure Brightness Meter',
                 id='pychron.fusions.co2.brightness_meter'
                 )

        return v

    def _setpoint_changed(self):
        t = Thread(target=self._start)
        t.start()

    def _start(self):
        if self._collect_baseline:
            self._collect_baseline = False
            if self.brightness_manager:
                self.brightness_manager.collect_baseline()
#                do_later(self._set_window)

        if abs(self.setpoint) < 0.001:
            self._collect_baseline = True

        self.set_brightness_setpoint(self.setpoint)

    def _pid_object_default(self):
        return self._load_pid_object()

    def _graph_default(self):
        g = StreamGraph(container_dict=dict(padding=5),)
        g.new_plot(data_limit=60 * 1000 / float(self.pid_loop_period))
        g.set_x_tracking(60)

        g.new_series()
        g.new_series()
        g.new_series()

        return g

    def _brightness_manager_default(self):


        b = BrightnessManager(laser_manager=self.parent,
                              parent=self.parent.stage_manager,
                              video=self.parent.stage_manager.video
                             )

        return b

    def _load_pid_object(self):
        p = os.path.join(paths.hidden_dir, 'brightness_pid_object')
        if os.path.isfile(p):
            self.info('loading pid object from {}'.format(p))
            try:
                with open(p, 'rb') as f:
                    po = pickle.load(f)
            except pickle.PickleError, e:
                self.info('error loading pid object from {}, {}'.format(p, e))
                po = PIDObject()
        else:
            po = PIDObject()

        return po

    def _dump_pid_object(self):

        try:
            p = os.path.join(paths.hidden_dir, 'brightness_pid_object')
            self.info('dumping pid object to {}'.format(p))
            with open(p, 'wb') as f:
                pickle.dump(self.pid_object, f)
        except pickle.PickleError:
            pass

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('bm')
    b = BrightnessPIDManager(parent=DummyParent())
    b.brightness_manager.detector.radius_mm = 2.25
    b.configure_traits()

#============= EOF =============================================
