#===============================================================================
# Copyright 2012 Jake Ross
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
from src.envisage.core.action_helper import open_manager, open_selector

#============= standard library imports ========================
#============= local library imports  ==========================

class FOpenLaserManagerAction(Action):
    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager)


class FOpenMotionControllerManagerAction(Action):

    def perform(self, event):
        man = self.get_manager(event)
        if man is not None:
            m = man.stage_manager.motion_configure_factory(view_style='full_view')
            app = self.window.application
            open_manager(app, m)


class FPowerMapAction(Action):
    name = 'Power Map'

    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            man = manager.get_power_map_manager()
            app = self.window.application
            open_manager(app, man)

class FPowerCalibrationAction(Action):
    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.power_calibration_manager)
#===============================================================================
# database selectors
#===============================================================================
class FOpenPowerCalibrationAction(Action):
    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            db = manager.get_power_calibration_database()
            open_selector(db, self.window.application)

class FOpenPowerMapAction(Action):
    name = 'Open Map Result'

    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            db = manager.get_power_map_manager().database
            open_selector(db, self.window.application)


class FOpenPowerRecordGraphAction(Action):
    name = 'Open Power Scan Result'

    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            db = manager.get_power_database()
            open_selector(db, self.window.application)


class FOpenVideoAction(Action):
    name = 'Open Video Result'

    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            db = manager.stage_manager.get_video_database()
            open_selector(db, self.window.application)

#===============================================================================
# initializations
#===============================================================================
class FInitializeBeamAction(Action):
    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            manager.do_motor_initialization('beam')


class FInitializeZoomAction(Action):
    def perform(self, event):
        manager = self.get_manager(event)
        if manager is not None:
            manager.do_motor_initialization('zoom')
#============= EOF =============================================
