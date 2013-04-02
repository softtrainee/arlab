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
from src.envisage.core.action_helper import open_manager
from src.lasers.plugins.fusions.fusions_actions import FOpenMotionControllerManagerAction, \
    FPowerMapAction, FPowerCalibrationAction, FOpenLaserManagerAction, \
    FOpenStageVisualizerAction, FOpenPowerCalibrationAction, \
    FLoadStageVisualizerAction, \
    FOpenVideoAction, FOpenPowerRecordGraphAction, FOpenPowerMapAction, \
    FOpenPatternAction, FNewPatternAction, LocalLaserAction, FMotorConfigureAction, \
    FExecutePatternAction, FConfigureBrightnessMeterAction, FPulseAction, \
    FOpticsAction
    # FInitializeZoomAction, FInitializeBeamAction, \

#============= standard library imports ========================

#============= local library imports  ==========================

class DiodeMixin(object):
    manager_name = 'fusions_diode'

# class DegasAction(DiodeMixin, LocalLaserAction):
#    def perform(self, event):
#        manager = self._get_manager(event)
#        if manager is not None:
#            man = manager.get_degas_manager()
#            app = self.window.application
#            open_manager(app, man)


class ConfigureWatlowAction(DiodeMixin, LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            t = manager.temperature_controller
            t.initialization_hook()
            app = self.window.application
            open_manager(app, t, view='configure_view')

#===============================================================================
# fusions action
#===============================================================================

class OpticsAction(DiodeMixin, FOpticsAction):
    pass

class PulseAction(DiodeMixin, FPulseAction):
    pass

class OpenLaserManagerAction(DiodeMixin, FOpenLaserManagerAction):
    pass

class OpenMotionControllerManagerAction(DiodeMixin, FOpenMotionControllerManagerAction):
    pass

class PowerMapAction(DiodeMixin, FPowerMapAction):
    pass

class PowerCalibrationAction(DiodeMixin, FPowerCalibrationAction):
    pass

class OpenStageVisualizerAction(DiodeMixin, FOpenStageVisualizerAction):
    pass

class LoadStageVisualizerAction(DiodeMixin, FLoadStageVisualizerAction):
    pass

#===============================================================================
# database selectors
#===============================================================================
class OpenPowerCalibrationAction(DiodeMixin, FOpenPowerCalibrationAction):
    pass

class OpenPowerMapAction(DiodeMixin, FOpenPowerMapAction):
    pass

class OpenPowerRecordGraphAction(DiodeMixin, FOpenPowerRecordGraphAction):
    pass

class OpenVideoAction(DiodeMixin, FOpenVideoAction):
    pass

class MotorConfigureAction(DiodeMixin, FMotorConfigureAction):
    pass

class ConfigureBrightnessMeterAction(DiodeMixin, FConfigureBrightnessMeterAction):
    pass
#===============================================================================
# initializations
#===============================================================================
# class InitializeBeamAction(DiodeMixin, FInitializeBeamAction):
#    pass
#
# class InitializeZoomAction(DiodeMixin, FInitializeZoomAction):
#    pass
#===============================================================================
# patterning
#===============================================================================
class OpenPatternAction(DiodeMixin, FOpenPatternAction):
    pass
class NewPatternAction(DiodeMixin, FNewPatternAction):
    pass
class ExecutePatternAction(DiodeMixin, FExecutePatternAction):
    pass
