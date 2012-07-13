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
from traits.api import Float, Property, Int
from traitsui.api import View, Item, Group, RangeEditor

#============= standard library imports ========================
#import math
#============= local library imports  ==========================
from src.hardware.axis import Axis


class AerotechAxis(Axis):
    '''
    '''
    feedrate = Float(enter_set=True, auto_set=False)
    metric_digits = Int
    mlow = Int(1)
    mhigh = Int(8)

    conversion_factor = Float(enter_set=True, auto_set=False)

    rms_current_sample_time = Property(Float(enter_set=True, auto_set=False))
    _rms_current_sample_time = Float

    def _validate_rms_current_sample_time(self, s):
        '''
            
        '''
        if 0 <= s <= 16383:
            nv = s
        else:
            nv = self._rms_current_sample_time
        return nv

    def _get_rms_current_sample_time(self):
        '''
        '''
        return self._rms_current_sample_time

    def _set_rms_current_sample_time(self, v):
        '''
     
        '''
        cmd = int('%i49' % self.id)
        self.parent.set_parameter(cmd, v)

#    def load_parameters_from_config(self, path):
#        '''
#      
#        '''
#        for key, value in self._get_parameters(path):
#            pass

    def load_parameters_from_device(self):
        '''
        '''
        if not self.parent.simulation:
            params = ['feedrate', (23, 24, 25, 26)]
            for p, pn in params:
                cmd = 'RP{}'
                n = pn
                if isinstance(pn, tuple):
                    n = pn[self.id - 1]
                cmd = cmd.format(n)

                self.parent.ask(cmd)
                value = 0
                setattr(p, value)

    def _feedrate_changed(self):
        '''
        '''
        n = (23, 24, 25, 26)[self.id - 1]
        self._set_parameter(n, self.feedrate)

    def _metric_digits_changed(self):
        '''
        '''
        n = (29, 47, 65, 83)[self.id - 1]

        self._set_parameter(n, self.metric_digits)

    def _conversion_factor_changed(self):
        '''
        '''
        n = int('%i00' % self.id)
        v = self.conversion_factor

#        machine_steps = 4000
#        prog_unit = 10
#
#        cf = (machine_steps / prog_unit) / math.pow(10, self.metric_digits)

        self._set_parameter(n, v)

    def _set_parameter(self, n, v):
        '''
            
        '''
        self.parent.set_parameter(n, v)

    def _anytrait_changed(self, name, old, new):
        '''
            
        '''
        #print name,old,new
        pass

    def traits_view(self):
        '''
        '''
        axis_config = Group(Item('conversion_factor'))
        planes = Group(Item('feedrate'),
                     Item('metric_digits', editor=RangeEditor(mode='spinner',
                                                             low_name='mlow',
                                                             high_name='mhigh')))
        traps = Group(Item('rms_current_sample_time'))
        return View(axis_config,
                    planes,
                    traps,
                    )
#============= EOF ====================================
