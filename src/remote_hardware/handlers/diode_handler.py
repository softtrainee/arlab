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
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.remote_hardware.errors.system_errors import InvalidArgumentsErrorCode
from laser_handler import LaserHandler


class DiodeHandler(LaserHandler):
    manager_name = 'Diode'

    def SetLaserPower(self, manager, data, *args):
        result = 'OK'
        try:
            p = float(data)
        except:
            return InvalidArgumentsErrorCode('SetLaserPower',
                                             data,
                                             logger=self)

        manager.set_laser_temperature(p)
        return result


#============= views ===================================
#============= EOF ====================================
