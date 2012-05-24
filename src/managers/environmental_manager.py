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
from traits.api import Float, Str
from traitsui.api import View, Item, VGroup
from pyface.timer.timer import Timer

#============= standard library imports ========================

#============= local library imports  ==========================
from manager import Manager
from pylab import hstack, mean, std, polyfit

class EnvironmentalManager(Manager):
    '''
    '''

    coolant_temp = Float
    coolant_average = Float
    coolant_std = Float
    coolant_trend = Str
    _coolant_temp_buffer_ = None

    humidity = Float
    ambient_temp = Float

    def __init__(self, *args, **kw):
        '''
 
        '''
        super(EnvironmentalManager, self).__init__(*args, **kw)
        self._coolant_temp_buffer_ = []

    def finish_loading(self):
        '''
        '''
        self._update_timer = Timer(30000, self._update_)

    def _update_(self):
        '''
        '''
        for g in dir(self):
            if g[:7] == 'update_':
                getattr(self, g)()

    def update_coolant_temp(self):
        '''
        '''
        buf = self._coolant_temp_buffer_
        width = 5
        chiller = self.get_device('thermo_rack')
        if chiller is not None:
            self.coolant_temp = nc = chiller.get_coolant_out_temperature()
            #update the coolant states
            buf = hstack((buf[-width:], [nc]))
            self.coolant_average = mean(buf)
            self.coolant_std = std(buf)

            self._coolant_temp_buffer_ = buf
            n = len(buf)
            if n > 2:
                slope, _intercept = polyfit(range(n), buf, 1)
                if slope < 0:
                    self.coolant_trend = 'Cooling'
                else:
                    self.coolant_trend = 'Warming'

    def traits_view(self):
        '''
        '''
        g = VGroup(Item('coolant_temp', label='Coolant Temp', style='readonly'),
                 Item('coolant_average', label='Avg.', format_str='%0.2f', style='readonly'),
                 Item('coolant_std', label='Std.', format_str='%0.2f', style='readonly'),
                 Item('coolant_trend', label='Trend', style='readonly'),

                 )

        v = View(g,
               resizable=True)

        return v
#============= views ===================================
#============= EOF ====================================
