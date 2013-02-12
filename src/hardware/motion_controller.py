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
from traits.api import Property, Dict, Float, Any, Instance
from traitsui.api import View, VGroup, Item, RangeEditor
from pyface.timer.api import Timer
#from src.helpers.timer import Timer
#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.hardware.core.core_device import CoreDevice
from src.hardware.core.motion.motion_profiler import MotionProfiler
import time


UPDATE_MS = 150


class MotionController(CoreDevice):
    '''
    '''
    axes = Dict
    xaxes_max = Property
    xaxes_min = Property
    yaxes_max = Property
    yaxes_min = Property
    zaxes_max = Property
    zaxes_min = Property

    group_parameters = None
    timer = None
    parent = Any

    x = Property(trait=Float(enter_set=True, auto_set=False),
               depends_on='_x_position')
    _x_position = Float
    y = Property(trait=Float(enter_set=True, auto_set=False),
               depends_on='_y_position')
    _y_position = Float

    z = Property(trait=Float(enter_set=True, auto_set=False),
           depends_on='_z_position')

    _z_position = Float
    z_progress = Float
    motion_profiler = Instance(MotionProfiler, ())

    groupobj = None
    def save_axes_parameters(self):
        pass

    def _motion_profiler_default(self):
        mp = MotionProfiler()
        if self.configuration_dir_path:
            p = os.path.join(self.configuration_dir_path, 'motion_profiler.cfg')
            mp.load(p)
        return mp

    def traits_view(self):
        return View(self.get_control_group())

    def update_axes(self):
        for a in self.axes:
            pos = self.get_current_position(a)
            if pos is not None:
                setattr(self, '_{}_position'.format(a), pos)

        self.parent.canvas.set_stage_position(self._x_position,
                                       self._y_position)

        self.z_progress = self._z_position

    def timer_factory(self, func=None):
        '''
        '''
        if self.timer is not None:
            self.timer.Stop()

        if func is None:
            func = self._inprogress_update
        self._not_moving_count = 0
        return Timer(UPDATE_MS, func)

    def _z_inprogress_update(self):
        '''
        '''
        if not self._moving_():
            self.timer.Stop()
        
        z = self.get_current_position('z')
        self.z_progress = z
        
#        if self._moving_():
#            z = self.get_current_position('z')
#            if z is not None:
#                self.z_progress = z
#        elif self._not_moving_count > 3:
#            self.timer.Stop()
#            self.z_progress = self.z
#
#        else:
#            self._not_moving_count += 1

    def _inprogress_update(self):
        '''
        '''
        if not self._moving_():
            self.timer.Stop()
            self.parent.canvas.clear_desired_position()
            time.sleep(0.1)
#        else:
        x = self.get_current_position('x')
        y = self.get_current_position('y')
#        self.info('setting x={:3f}, y={:3f}'.format(x, y))
#        do_later(self.parent.canvas.set_stage_position, x, y)
        self.parent.canvas.set_stage_position(x, y)


    def _get_x(self):
        '''
        '''
        return self._x_position

    def _get_y(self):
        '''
        '''
        return self._y_position

    def _get_z(self):
        '''
        '''
        return self._z_position

    def _validate(self, v, key, cur):
        '''
        '''
        mi = self.axes[key].negative_limit
        ma = self.axes[key].positive_limit

        try:
            v = float(v)
            if not mi <= v <= ma:
                v = None

            if v is not None:
                if abs(v - cur) <= 0.001:
                    v = None
        except ValueError:

            v = None

#        print 'validate', min, max, v
        return v

    def _validate_x(self, v):
        '''

        '''
        return self._validate(v, 'x', self._x_position)

    def _validate_y(self, v):
        '''

        '''
        return self._validate(v, 'y', self._y_position)

#    def _validate_z(self, v):
#        '''

#        '''
#        return self._validate(v, 'z', self._z_position)
    def _validate_z(self, v):
        '''
        '''
        return self._validate(v, 'z', self._z_position)

    def set_z(self, v, **kw):
        self.single_axis_move('z', v, **kw)
        self._z_position = v
        self.axes['z'].position=v

    def _set_z(self, v):
        '''
        '''
        if v is not None:
            self.set_z(v)

    def _set_x(self, v):
        '''
        '''
        if v is not None:
            self.single_axis_move('x', v)
            self._x_position = v
            self.axes['x'].position=v

    def _set_y(self, v):
        '''

        '''
        if v is not None:
            self.single_axis_move('y', v)
            self._y_position = v
            self.axes['y'].position=v

    def get_current_position(self, *args, **kw):
        '''

        '''
        return 0

    def single_axis_move(self, *args, **kw):
        '''
        '''
        pass
#    def _moving_(self):
#        pass

    def define_home(self):
        '''
        '''
        pass

    def get_control_group(self):
        g = VGroup(show_border=True,
                   label='Axes')

        keys = self.axes.keys()
        keys.sort()
        for k in keys:

            editor = RangeEditor(low_name='{}axes_min'.format(k),
                                  high_name='{}axes_max'.format(k),
                                  mode='slider',
                                  format='%0.3f')

            g.content.append(Item(k, editor=editor))
            if k == 'z':
                g.content.append(Item('z_progress', show_label=False,
                                      editor=editor,
                                      enabled_when='0'
                                      ))
        return g

    def set_single_axis_motion_parameters(self, *args, **kw):
        pass

    def block(self, *args, **kw):
        pass
    def linear_move(self, *args, **kw):
        pass
    def set_home_position(self,*args, **kw):
        pass
    def axes_factory(self, config=None):
        if config is None:

            config = self.get_configuration(self.config_path)

        mapping = self.config_get(config, 'General', 'mapping')
        if mapping is not None:
            mapping = mapping.split(',')
        else:
            mapping = 'x,y,z'

        lp = self.config_get(config, 'General', 'loadposition')
        if lp is not None:
            loadposition = [float(f) for f in lp.split(',')]
        else:
            loadposition = [0, 0, 0]

        config_path = self.configuration_dir_path
        for i, a in enumerate(mapping):
            self.info('loading axis {},{}'.format(i, a))
            limits = [float(v) for v in config.get('Axes Limits', a).split(',')]
            na = self._axis_factory(config_path,
                                  name=a,
                                  id=i + 1,
                                  negative_limit=limits[0],
                                  positive_limit=limits[1],
                                  loadposition=loadposition[i]
                                  )

            self.axes[a] = na
    def _get_xaxes_max(self):
        '''
        '''
        return self.axes['x'].positive_limit if self.axes.has_key('x') else 0

    def _get_xaxes_min(self):
        '''
        '''
        return self.axes['x'].negative_limit if self.axes.has_key('x') else 0

    def _get_yaxes_min(self):
        '''
        '''
        return self.axes['y'].negative_limit if self.axes.has_key('y') else 0

    def _get_yaxes_max(self):
        '''
        '''
        return self.axes['y'].positive_limit if self.axes.has_key('y') else 0

    def _get_zaxes_min(self):
        '''
        '''
        return self.axes['z'].negative_limit if self.axes.has_key('z') else 0

    def _get_zaxes_max(self):
        '''
        '''
        return self.axes['z'].positive_limit if self.axes.has_key('z') else 0
    
    def _sign_correct(self, val, key, ratio=True):
        '''
        '''
        axis = self.axes[key]
        r = 1
        if ratio:
            r = axis.drive_ratio
#            self.info('using drive ratio {}={}'.format(key, r))
        
        return val * axis.sign * r
#============= EOF ====================================
