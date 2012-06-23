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
from traits.api import Bool, on_trait_change
from traitsui.api import View, Item, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.motion_controller_managers.motion_controller_manager import MotionControllerManager
class AerotechMotionControllerManager(MotionControllerManager):
    '''
    '''
    _auto_enable_x = Bool
    _auto_enable_y = Bool
    _auto_enable_z = Bool
    _auto_enable_u = Bool

    @on_trait_change('_auto_enable_+')
    def _auto_enable(self, n, value):
        '''
     
        '''
        value = ' '.join([a for a in ['X', 'Y', 'Z', 'U'] if getattr(self, '_auto_enable_%s' % a.lower())])
        self.motion_controller.set_parameter(600, value)

#============= views ===================================
    def traits_view(self):
        '''
        '''
        for a in self._get_axes():
            a.load_parameters_from_device()

        v = super(AerotechMotionControllerManager, self).traits_view()
        system_grp = VGroup(Item('_auto_enable_x', label='X'),
                                Item('_auto_enable_y', label='Y'),
                                Item('_auto_enable_z', label='Z'),
                                Item('_auto_enable_u', label='U'),
                                label='Auto Enable Axes')
        return View(system_grp, v.content)
#============= EOF ====================================
