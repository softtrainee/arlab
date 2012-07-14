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
from src.lasers.plugins.fusions.fusions_actions import FInitializeZoomAction,\
    FInitializeBeamAction, FOpenVideoAction, FOpenPowerRecordGraphAction,\
    FOpenPowerMapAction, FOpenPowerCalibrationAction, FLoadStageVisualizerAction,\
    FOpenStageVisualizerAction, FPowerCalibrationAction, FPowerMapAction,\
    FOpenMotionControllerManagerAction, FOpenLaserManagerAction
#from src.database.adapters.power_adapter import PowerAdapter
#from src.helpers.paths import co2laser_db
#from traits.api import on_trait_change

#============= standard library imports ========================

#============= local library imports  ==========================

def get_manager(_, event, app=None):

    if app is None:
        app = event.window.application
    base = 'src.lasers.laser_managers.{}'

    manager = app.get_service(base.format('fusions_co2_manager.FusionsCO2Manager'))

    return manager


class ConfigureBrightnessMeterAction(Action):
    def perform(self, event):
        manager = get_manager(None, event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.brightness_meter)

#===============================================================================
# ##fusions action
#===============================================================================
class OpenLaserManagerAction(FOpenLaserManagerAction):
    name = 'Open Laser Manager'
    get_manager = get_manager

class OpenMotionControllerManagerAction(FOpenMotionControllerManagerAction):
    get_manager = get_manager

class PowerMapAction(FPowerMapAction):
    get_manager = get_manager


class PowerCalibrationAction(FPowerCalibrationAction):
    get_manager = get_manager
    
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
class InitializeBeamAction(FInitializeBeamAction):
    get_manager = get_manager

class InitializeZoomAction(FInitializeZoomAction):
    get_manager = get_manager


#===============================================================================
# unused
#===============================================================================
#class PowerScanAction(Action):
#    name = 'Open Power Scan'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.show_power_scan()
#
#
#class StepHeatAction(Action):
#    name = 'Open Step Heater'
#    enabled = False
#
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
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.get_pulse_manager()
#            open_manager(self.window.application,
#                         man, view='standalone_view')
#class OpenPowerScanGraphAction(Action):
#    name = 'Open Power Scan Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.graph_manager.open_graph('powerscan')
#class MoveLoadPositionAction(Action):
#    name = 'Loading Position'
#    description = 'Move to loading position'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.move_to_load_position()
#class ExecutePatternAction(Action):
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.stage_manager.pattern_manager.execute_pattern()
#
#
#class OpenPatternManagerAction(Action):
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            app = self.window.application
#            open_manager(app,
#                         manager.stage_manager.pattern_manager, view='pattern_maker_view')


#class PowerMapAction(Action):
#    name = 'Power Map'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.get_power_map_manager()
#            app = self.window.application
#            open_manager(app, man)
#
#class PowerCalibrationAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            app = self.window.application
#            open_manager(app, manager.power_calibration_manager)
#
##===============================================================================
## database selectors
##===============================================================================
#class OpenPowerCalibrationAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.get_power_calibration_database()
#            open_selector(db, self.window.application)
#
#
#class OpenPowerMapAction(Action):
#    name = 'Open Map Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.get_power_map_manager().database
#            open_selector(db, self.window.application)
#
#
#class OpenPowerRecordGraphAction(Action):
#    name = 'Open Power Scan Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.get_power_database()
#            open_selector(db, self.window.application)
#
#
#class OpenVideoAction(Action):
#    name = 'Open Video Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.stage_manager.get_video_database()
#            open_selector(db, self.window.application)
#
##===============================================================================
## initializations
##===============================================================================
#class InitializeBeamAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.do_motor_initialization('beam')
#
#
#class InitializeZoomAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.do_motor_initialization('zoom')



