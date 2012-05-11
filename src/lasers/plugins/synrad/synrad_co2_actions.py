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
from pyface.action.api import Action
from src.envisage.core.action_helper import open_manager
#from traits.api import on_trait_change

#============= standard library imports ========================

#============= local library imports  ==========================
def get_manager(event):
        app = event.window.application
        base = 'src.managers.laser_managers.%s'
        manager = app.get_service(base % 'synrad_co2_manager.SynradCO2Manager')

        return manager

#class OpenJogManagerAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            open_manager(manager.stage_manager.jog_manager)

class ConfigStageControllerAction(Action):
    def perform(self, event):
        manager = get_manager(event)

        open_manager(manager.stage_manager.motion_controller_manager)
#class OpenStageManagerAction(Action):
#    name = 'Open Stage Manager'
#
#    enabled = True
#
#    def __init__(self, *args, **kw):
#        super(OpenStageManagerAction, self).__init__(*args, **kw)
#        v = self.window.get_view_by_id('fusions.stage')
#        if v is not None:
#            v.on_trait_change(self.update, 'visible')
#
#    def update(self, obj, name, old, new):
#        self.enabled = not new
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.stage_manager
#            man.initialize_stage()
#            man.controllable = True
#            open_manager(man)
#            #manager.show_stage_manager()#parent = self.window.control)

class OpenLaserManagerAction(Action):
    name = 'Open Laser Manager'
    enabled = True

    def __init__(self, *args, **kw):
        super(OpenLaserManagerAction, self).__init__(*args, **kw)
        v = self.window.get_view_by_id('synrad.control')
        if v is not None:
            v.on_trait_change(self.update, 'visible')

    def update(self, obj, name, old, new):
        self.enabled = not new

    def perform(self, event):
        man = get_manager(event)
        if man is not None:
            open_manager(man)

class MoveLoadPositionAction(Action):
    name = 'Loading Position'
    description = 'Move to loading position'
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.move_to_load_position()

class PowerScanAction(Action):
    name = 'Open Power Scan'
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.show_power_scan()

class PowerMapAction(Action):
    name = 'Power Map'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            man = manager.get_power_map_manager()
            open_manager(man)

class OpenPowerScanGraphAction(Action):
    name = 'Open Power Scan Result'
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.graph_manager.open_power_scan_graph()

class OpenPowerMapAction(Action):
    name = 'Open Map Result'
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.graph_manager.open_power_map()



#============= EOF ====================================
