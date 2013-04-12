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
from src.lasers.laser_managers.ilaser_manager import ILaserManager
from src.lasers.laser_managers.pychron_laser_manager import PychronLaserManager

#============= standard library imports ========================
#============= local library imports  ==========================
class BaseLaserAction(Action):
    manager_name = None
    def _get_manager(self, event, app=None):
        if app is None:
            app = event.window.application

        manager = app.get_service(ILaserManager,
                                  'name=="{}"'.format(self.manager_name),
                                  )
        return manager

class LocalLaserAction(BaseLaserAction):
    client_action = False
    def __init__(self, window=None, *args, **kw):
        super(LocalLaserAction, self).__init__(window=window, *args, **kw)
        man = self._get_manager(None, app=self.window.application)
        if isinstance(man, PychronLaserManager) and not self.client_action:
            self.enabled = False


class FOpticsAction(LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.optics_view)

class FPulseAction(LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.pulse)

class FOpenLaserManagerAction(BaseLaserAction):
    accelerator = 'Ctrl+L'
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager)


class FOpenMotionControllerManagerAction(LocalLaserAction):

    def perform(self, event):
        man = self._get_manager(event)
        if man is not None:
            m = man.stage_manager.motion_configure_factory(view_style='full_view')
            app = self.window.application
            open_manager(app, m)


class FPowerMapAction(LocalLaserAction):
    name = 'Power Map'

    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            man = manager.get_power_map_manager()
            app = self.window.application
            open_manager(app, man)

class FPowerCalibrationAction(LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.power_calibration_manager)


class FOpenStageVisualizerAction(LocalLaserAction):
#    def __init__(self, *args, **kw):
#        print 'sffsadf', args, kw
#        super(FStageVisualizerAction, self).__init__(*args, **kw)
#
#        man = self._get_manager(None, window=kw['window'])
# #        print man.use_video?
#        self.enabled_when = 'enabled'
#        self.enabled = man.use_video
#        man.on_trait_change(self.update_enabled, 'use_video')

#    def update_enabled(self, obj, name, new):
#        if name == 'use_video':
#            self.enabled = new
#        print self.enabled

    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.stage_manager.visualizer)

class FLoadStageVisualizerAction(LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            visualizer = manager.stage_manager.visualizer
            visualizer.load_visualization()
            open_manager(app, visualizer)


#===============================================================================
# database selectors
#===============================================================================
class FOpenPowerCalibrationAction(LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            db = manager.get_power_calibration_database()
            if db:
                open_selector(db, self.window.application)

class FOpenPowerMapAction(LocalLaserAction):
    name = 'Open Map Result'

    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            db = manager.get_power_map_database()
            if db:
                open_selector(db, self.window.application)


class FOpenPowerRecordGraphAction(LocalLaserAction):
    name = 'Open Power Scan Result'

    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            db = manager.get_power_database()
            if db:
                open_selector(db, self.window.application)


class FOpenVideoAction(LocalLaserAction):
    name = 'Open Video Result'

    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            db = manager.stage_manager.get_video_database()
            if db:
                open_selector(db, self.window.application)


class FMotorConfigureAction(LocalLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            manager.open_motor_configure()

class FConfigureBrightnessMeterAction(LocalLaserAction):
    def __init__(self, *args, **kw):
        super(FConfigureBrightnessMeterAction, self).__init__(*args, **kw)

        man = self._get_manager(None, app=self.window.application)

        man.on_trait_change(self._update_enable, 'use_video')
        if man.use_video:
            self.enabled = False

    def _update_enable(self, new):
        self.enabled = new

    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.brightness_meter)
#===============================================================================
# initializations
#===============================================================================
# class FInitializeBeamAction(LocalLaserAction):
#    def perform(self, event):
#        manager = self._get_manager(event)
#        if manager is not None:
#            manager.do_motor_initialization('beam')
#
#
# class FInitializeZoomAction(LocalLaserAction):
#    def perform(self, event):
#        manager = self._get_manager(event)
#        if manager is not None:
#            manager.do_motor_initialization('zoom')

#===============================================================================
# patterning
#===============================================================================
class FOpenPatternAction(BaseLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            manager.open_pattern_maker()

class FNewPatternAction(BaseLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            manager.new_pattern_maker()

class FExecutePatternAction(BaseLaserAction):
    def perform(self, event):
        manager = self._get_manager(event)
        if manager is not None:
            manager.execute_pattern()

#============= EOF =============================================
