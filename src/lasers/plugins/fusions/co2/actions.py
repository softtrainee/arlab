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
from src.lasers.plugins.fusions.fusions_actions import FOpenVideoAction, FOpenPowerRecordGraphAction, \
    FOpenPowerMapAction, FOpenPowerCalibrationAction, FLoadStageVisualizerAction, \
    FOpenStageVisualizerAction, FPowerCalibrationAction, FPowerMapAction, \
    FOpenMotionControllerManagerAction, FOpenLaserManagerAction, \
    FOpenPatternAction, FNewPatternAction, FMotorConfigureAction, \
    FExecutePatternAction, FConfigureBrightnessMeterAction

#============= standard library imports ========================

#============= local library imports  ==========================

class CO2Mixin(object):
    manager_name = 'fusions_co2'

class ConfigureBrightnessMeterAction(CO2Mixin, FConfigureBrightnessMeterAction):
    pass

class MotorConfigureAction(CO2Mixin, FMotorConfigureAction):
    pass
#===============================================================================
# ##fusions action
#===============================================================================
class OpenLaserManagerAction(CO2Mixin, FOpenLaserManagerAction):
    name = 'Open Laser Manager'

class OpenMotionControllerManagerAction(CO2Mixin, FOpenMotionControllerManagerAction):
    pass

class PowerMapAction(CO2Mixin, FPowerMapAction):
    pass


class PowerCalibrationAction(CO2Mixin, FPowerCalibrationAction):
    pass

class OpenStageVisualizerAction(CO2Mixin, FOpenStageVisualizerAction):
    pass

class LoadStageVisualizerAction(CO2Mixin, FLoadStageVisualizerAction):
    pass
#===============================================================================
# database selectors
#===============================================================================
class OpenPowerCalibrationAction(CO2Mixin, FOpenPowerCalibrationAction):
    pass

class OpenPowerMapAction(CO2Mixin, FOpenPowerMapAction):
    pass

class OpenPowerRecordGraphAction(CO2Mixin, FOpenPowerRecordGraphAction):
    pass

class OpenVideoAction(CO2Mixin, FOpenVideoAction):
    pass

#===============================================================================
# initializations
#===============================================================================
#class InitializeBeamAction(CO2Mixin, FInitializeBeamAction):
#    pass
#
#class InitializeZoomAction(CO2Mixin, FInitializeZoomAction):
#    pass

#===============================================================================
# patterning
#===============================================================================
class OpenPatternAction(CO2Mixin, FOpenPatternAction):
    pass
class NewPatternAction(CO2Mixin, FNewPatternAction):
    pass
class ExecutePatternAction(CO2Mixin, FExecutePatternAction):
    pass
#===============================================================================
# unused
#===============================================================================
#class PowerScanAction(CO2Mixin, Action):
#    name = 'Open Power Scan'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.show_power_scan()
#
#
#class StepHeatAction(CO2Mixin, Action):
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
#class PulseAction(CO2Mixin, Action):
#    name = 'Power Map'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.get_pulse_manager()
#            open_manager(self.window.application,
#                         man, view='standalone_view')
#class OpenPowerScanGraphAction(CO2Mixin, Action):
#    name = 'Open Power Scan Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.graph_manager.open_graph('powerscan')
#class MoveLoadPositionAction(CO2Mixin, Action):
#    name = 'Loading Position'
#    description = 'Move to loading position'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.move_to_load_position()
#class ExecutePatternAction(CO2Mixin, Action):
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.stage_manager.pattern_manager.execute_pattern()
#
#
#class OpenPatternManagerAction(CO2Mixin, Action):
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            app = self.window.application
#            open_manager(app,
#                         manager.stage_manager.pattern_manager, view='pattern_maker_view')


#class PowerMapAction(CO2Mixin, Action):
#    name = 'Power Map'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.get_power_map_manager()
#            app = self.window.application
#            open_manager(app, man)
#
#class PowerCalibrationAction(CO2Mixin, Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            app = self.window.application
#            open_manager(app, manager.power_calibration_manager)
#
##===============================================================================
## database selectors
##===============================================================================
#class OpenPowerCalibrationAction(CO2Mixin, Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.get_power_calibration_database()
#            open_selector(db, self.window.application)
#
#
#class OpenPowerMapAction(CO2Mixin, Action):
#    name = 'Open Map Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.get_power_map_manager().database
#            open_selector(db, self.window.application)
#
#
#class OpenPowerRecordGraphAction(CO2Mixin, Action):
#    name = 'Open Power Scan Result'
#
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            db = manager.get_power_database()
#            open_selector(db, self.window.application)
#
#
#class OpenVideoAction(CO2Mixin, Action):
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
#class InitializeBeamAction(CO2Mixin, Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.do_motor_initialization('beam')
#
#
#class InitializeZoomAction(CO2Mixin, Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            manager.do_motor_initialization('zoom')



