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
#from pyface.action.api import Action
from src.envisage.core.action_helper import open_manager
from src.lasers.plugins.fusions.fusions_actions import FOpenMotionControllerManagerAction, \
    FPowerMapAction, FPowerCalibrationAction, FOpenLaserManagerAction, \
    FOpenStageVisualizerAction, FOpenPowerCalibrationAction, \
    FLoadStageVisualizerAction, \
    FOpenVideoAction, FOpenPowerRecordGraphAction, FOpenPowerMapAction, \
    FOpenPatternManagerAction, LaserAction, FMotorConfigureAction
    #FInitializeZoomAction, FInitializeBeamAction, \
from src.lasers.laser_managers.laser_manager import ILaserManager
#from traits.api import on_trait_change

#============= standard library imports ========================

#============= local library imports  ==========================

def get_manager(_, event, app=None, window=None):
    if window is not None:
        app = window.application
    elif app is None:
        app = event.window.application

    manager = app.get_service(ILaserManager,
                              'name=="fusions_uv"',
                              )
    return manager


#class DegasAction(LaserAction):
#    def perform(self, event):
#        manager = get_manager(None, event)
#        if manager is not None:
#            man = manager.get_degas_manager()
#            app = self.window.application
#            open_manager(app, man)
#
#
#class ConfigureWatlowAction(LaserAction):
#    def perform(self, event):
#        manager = get_manager(None, event)
#        if manager is not None:
#            t = manager.temperature_controller
#            t.initialization_hook()
#            app = self.window.application
#            open_manager(app,
#                         t, view='configure_view')

#===============================================================================
# ##fusions action
#===============================================================================

#from ..fusions_actions import FOpenLaserManagerAction
class OpenLaserManagerAction(FOpenLaserManagerAction):
    get_manager = get_manager


#from ..fusions_actions import FOpenMotionControllerManagerAction
class OpenMotionControllerManagerAction(FOpenMotionControllerManagerAction):
    get_manager = get_manager


#from ..fusions_actions import FPowerMapAction
class PowerMapAction(FPowerMapAction):
    get_manager = get_manager


#from ..fusions_actions import FPowerCalibrationAction
class PowerCalibrationAction(FPowerCalibrationAction):
    get_manager = get_manager

#from ..fusions_actions import FStageVisualizerAction
class OpenStageVisualizerAction(FOpenStageVisualizerAction):
    get_manager = get_manager

class LoadStageVisualizerAction(FLoadStageVisualizerAction):
    get_manager = get_manager

#===============================================================================
# database selectors
#===============================================================================
class OpenPowerCalibrationAction(FOpenPowerCalibrationAction):
    get_manager = get_manager

class OpenPowerMapAction(FOpenPowerMapAction):
    get_manager = get_manager

class OpenPowerRecordGraphAction(FOpenPowerRecordGraphAction):
    get_manager = get_manager

class OpenVideoAction(FOpenVideoAction):
    get_manager = get_manager

#===============================================================================
# initializations
#===============================================================================
#class InitializeBeamAction(FInitializeBeamAction):
#    get_manager = get_manager
#
#class InitializeZoomAction(FInitializeZoomAction):
#    get_manager = get_manager
class MotorConfigureAction(FMotorConfigureAction):
    get_manager = get_manager
#===============================================================================
# patterning
#===============================================================================
class OpenPatternManagerAction(FOpenPatternManagerAction):
    get_manager = get_manager
#===============================================================================
# unused
#===============================================================================
#class MoveLoadPositionAction(Action):
#    name = 'Loading Position'
#    description = 'Move to loading position'
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.move_to_load_position()
#
#class PowerScanAction(Action):
#    name = 'Open Power Scan'
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.show_power_scan()
#
#class StepHeatAction(Action):
#    name = 'Open Step Heater'
#    enabled = False
#    def __init__(self, *args, **kw):
#        super(StepHeatAction, self).__init__(*args, **kw)
#
#        man = get_manager(None, self.window.application)
#        if 'Diode' in man.__class__.__name__:
#            self.enabled = True
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.show_step_heater()
#class PulseAction(Action):
#    name = 'Power Map'
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.get_pulse_manager()
#            app = self.window.application
#            open_manager(app, man, view='standalone_view')
#
#class PowerMapAction(Action):
#    name = 'Power Map'
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.get_power_map_manager()
#            app = self.window.application
#            open_manager(app, man)#, view = 'canvas_view')
#
#class OpenPowerScanGraphAction(Action):
#    name = 'Open Power Scan Result'
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.graph_manager.open_graph('powerscan')
#
#class OpenPowerMapAction(Action):
#    name = 'Open Map Result'
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
##            manager.graph_manager.open_power_map()
#            manager.graph_manager.open_graph('powermap')
#class OpenCalibrationManagerAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.stage_manager.calibration_manager
#            app = self.window.application
#            open_manager(app, man)
#class ExecutePatternAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.stage_manager.pattern_manager.execute_pattern()
#
#class OpenPatternManagerAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            app = self.window.application
#            open_manager(app,
#                         manager.stage_manager.pattern_manager, view='pattern_maker_view')
#
#class OpenCalibrationManagerAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.stage_manager.calibration_manager
#            open_manager(man)
