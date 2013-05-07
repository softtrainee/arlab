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
from traits.api import HasTraits
from traitsui.api import View, UItem, Group, InstanceEditor, HGroup, \
    EnumEditor
from pyface.tasks.traits_task_pane import TraitsTaskPane
from pyface.tasks.traits_dock_pane import TraitsDockPane
#============= standard library imports ========================
#============= local library imports  ==========================
class BaseLaserPane(TraitsTaskPane):
    def traits_view(self):
        v = View(UItem('stage_manager', style='custom'))
        return v


class ControlPane(TraitsDockPane):
    def traits_view(self):
        def SItem(name, **kw):
            return UItem('object.stage_manager.{}'.format(name), **kw)

        agrp = SItem('stage_controller', style='custom')
        pgrp = Group(
                     SItem('calibrated_position_entry',
                           tooltip='Enter a positon e.g 1 for a hole, or 3,4 for X,Y'
                           ),
                     label='Calibrated Position',
                     show_border=True)
        hgrp = HGroup(SItem('stop_button'),
                      SItem('home'),
                      SItem('home_option', editor=EnumEditor(name='object.stage_manager.home_options'))
                      )
        cgrp = Group(
                     SItem('canvas',
                           editor=InstanceEditor(view='config_view'),
                           style='custom'),
                     SItem('points_programmer',
                          label='Points',
                          style='custom'),
                     SItem('tray_calibration_manager',
                          label='Calibration',
                          style='custom'),
                     layout='tabbed'
                     )
        v = View(agrp,
                 hgrp,
                 pgrp,
                 cgrp
                 )
        return v

class FusionsDiodePane(BaseLaserPane):
    pass

class FusionsDiodeControlPane(ControlPane):
    id = 'fusions.diode.control'
    name = 'Control'
# FusionsDiodePane = BaseLaserPane

# FusionsDiodeControlPane = ControlPane
#============= EOF =============================================
