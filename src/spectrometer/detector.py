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
from traits.api import  Float, Str, Bool, Property, Color
from traitsui.api import View, Item, VGroup, HGroup, spring, Label
from src.spectrometer.spectrometer_device import SpectrometerDevice

#============= standard library imports ========================

#============= local library imports  ==========================
charge = 1.6021764874e-19
class Detector(SpectrometerDevice):
    name = Str
    relative_position = Float(1)

    deflection = Property(Float(enter_set=True, auto_set=False), depends_on='_deflection')
    _deflection = Float

    intensity = Float
    active = Bool(True)

    color = Color
    isotope = Str

    def __repr__(self):
        return self.name

    def finish_loading(self):
        self.read_deflection()

    def _set_deflection(self, v):
        self._deflection = v
        self.microcontroller.ask('SetDeflection {},{}'.format(self.name,
                                                                   v))
    def _get_deflection(self):
        return self._deflection

    def read_deflection(self):
        r = self.microcontroller.ask('GetDeflection {}'.format(self.name))
        try:
            self._deflection = float(r)
        except ValueError:
            pass

    def traits_view(self):
        v = View(VGroup(
                        HGroup(
                                Item('name', style='readonly'),
                                Item('isotope'),
                                spring,
                                Item('active',),
                                Item('deflection'),
                                Item('color', style='readonly'),
                                show_labels=False
                                )
                      )
               )

        return v
if __name__ == '__main__':
    d = Detector()


#============= EOF =============================================
#    def calc_deflection(self, ht):
#        ht *= 1000 #accelerating voltage V
#        mass = 39.962
#        L = 1
#        velocity = math.sqrt(2 * charge * ht / mass)
#        flight_time = L / velocity
#        d = 0.1
#        E = -self._deflection / d
#        F = charge * E
#        delta = 0.5 * math.sqrt(F / mass) * flight_time ** 2
