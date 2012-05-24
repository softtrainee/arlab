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
#from src.database.adapters.power_adapter import PowerAdapter
#from src.helpers.paths import co2laser_db
#from traits.api import on_trait_change

#============= standard library imports ========================

#============= local library imports  ==========================


def get_manager(event, app=None):

    if app is None:
        app = event.window.application
    base = 'src.lasers.laser_managers.{}'

    manager = app.get_service(base.format('fusions_co2_manager.FusionsCO2Manager'))

    return manager

def open_selector(db, app):
    db.application = app
    db.connect()
    s = db._selector_factory()
    open_manager(app, s)

class ExecutePatternAction(Action):

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.stage_manager.pattern_manager.execute_pattern()


class OpenPatternManagerAction(Action):

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app,
                         manager.stage_manager.pattern_manager, view='pattern_maker_view')

#class OpenCalibrationManagerAction(Action):
#    def perform(self, event):
#        manager = get_manager(event)
#        if manager is not None:
#            man = manager.stage_manager.calibration_manager
#            open_manager(man)

class OpenMotionControllerManagerAction(Action):

    def perform(self, event):
        man = get_manager(event)
        if man is not None:
            m = man.stage_manager.motion_configure_factory(view_style='full_view')
            app = self.window.application
            open_manager(app, m)


class OpenLaserManagerAction(Action):
    name = 'Open Laser Manager'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            man = manager
            app = self.window.application
            open_manager(app, man)


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


class StepHeatAction(Action):
    name = 'Open Step Heater'
    enabled = False

    def __init__(self, *args, **kw):
        super(StepHeatAction, self).__init__(*args, **kw)

        man = get_manager(None, self.window.application)
        if 'Diode' in man.__class__.__name__:
            self.enabled = True

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.show_step_heater()
#------------------------------------------------------------------------------ 


class PulseAction(Action):
    name = 'Power Map'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            man = manager.get_pulse_manager()
            open_manager(self.window.application,
                         man, view='standalone_view')


class PowerMapAction(Action):
    name = 'Power Map'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            man = manager.get_power_map_manager()
            app = self.window.application
            open_manager(app, man)#, view = 'canvas_view')


class OpenPowerScanGraphAction(Action):
    name = 'Open Power Scan Result'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            manager.graph_manager.open_graph('powerscan')


class OpenPowerMapAction(Action):
    name = 'Open Map Result'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
#            from src.database.adapters.power_map_adapter import PowerMapAdapter
#            db = PowerMapAdapter(dbname=co2laser_db,
#                                 kind='sqlite'
##                                password='Argon',
#                                )
            db = manager.get_power_map_manager().database
            open_selector(db, self.window.application)

#            manager.graph_manager.open_power_map()
#            manager.graph_manager.open_graph('powermap')


class OpenPowerRecordGraphAction(Action):
    name = 'Open Power Scan Result'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
#            db = PowerAdapter(dbname='co2laserdb',
#                                password='Argon')
            db = manager.get_power_database()
            open_selector(db, self.window.application)
#            manager.graph_manager.open_graph('powerrecord')

class OpenVideoAction(Action):
    name = 'Open Video Result'

    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
#            db = PowerAdapter(dbname='co2laserdb',
#                                password='Argon')
            db = manager.stage_manager.get_video_database()
            open_selector(db, self.window.application)
#            manager.graph_manager.open_graph('powerrecord')

class ConfigureBrightnessMeterAction(Action):
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            app = self.window.application
            open_manager(app, manager.brightness_meter)

