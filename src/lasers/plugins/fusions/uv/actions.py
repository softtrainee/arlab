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
from src.lasers.plugins.fusions.fusions_actions import FOpenMotionControllerManagerAction, \
    FPowerMapAction, FPowerCalibrationAction, FOpenLaserManagerAction, \
    FOpenStageVisualizerAction, FOpenPowerCalibrationAction, \
    FLoadStageVisualizerAction, \
    FOpenVideoAction, FOpenPowerRecordGraphAction, FOpenPowerMapAction, \
    FOpenPatternAction, FNewPatternAction, FMotorConfigureAction, \
    FExecutePatternAction, FOpticsAction, FPulseAction, BaseLaserAction
from src.envisage.core.action_helper import open_manager
    # FInitializeZoomAction, FInitializeBeamAction, \

#============= standard library imports ========================

#============= local library imports  ==========================
class UVMixin(object):
    manager_name = 'fusions_uv'
class MosaicCollectAction(UVMixin, BaseLaserAction):
    def perform(self, event):
        man = self._get_manager(event)
        app = self.window.application
        open_manager(app, man.stage_manager.mosaic_manager)
#===============================================================================
# uv actions
#===============================================================================
class OpenGasHandlingAction(UVMixin, BaseLaserAction):
    accelerator = 'Ctrl+1'
    def perform(self, event):
        man = self._get_manager(event)

        open_manager(event.window.application, man.gas_handler)
#===============================================================================
# fusions action
#===============================================================================

class OpticsAction(UVMixin, FOpticsAction):
    pass
class PulseAction(UVMixin, FPulseAction):
    pass

class OpenLaserManagerAction(UVMixin, FOpenLaserManagerAction):
    pass

class OpenMotionControllerManagerAction(UVMixin, FOpenMotionControllerManagerAction):
    pass

class PowerMapAction(UVMixin, FPowerMapAction):
    pass

class PowerCalibrationAction(UVMixin, FPowerCalibrationAction):
    pass

class OpenStageVisualizerAction(UVMixin, FOpenStageVisualizerAction):
    pass

class LoadStageVisualizerAction(UVMixin, FLoadStageVisualizerAction):
    pass

#===============================================================================
# database selectors
#===============================================================================
class OpenPowerCalibrationAction(UVMixin, FOpenPowerCalibrationAction):
    pass

class OpenPowerMapAction(UVMixin, FOpenPowerMapAction):
    pass

class OpenPowerRecordGraphAction(UVMixin, FOpenPowerRecordGraphAction):
    pass

class OpenVideoAction(UVMixin, FOpenVideoAction):
    pass

#===============================================================================
# initializations
#===============================================================================
# class InitializeBeamAction(UVMixin, FInitializeBeamAction):
#    pass
#
# class InitializeZoomAction(UVMixin, FInitializeZoomAction):
#    pass
class MotorConfigureAction(UVMixin, FMotorConfigureAction):
    pass
#===============================================================================
# patterning
#===============================================================================
class OpenPatternAction(UVMixin, FOpenPatternAction):
    pass

class NewPatternAction(UVMixin, FNewPatternAction):
    pass

class ExecutePatternAction(UVMixin, FExecutePatternAction):
    pass
