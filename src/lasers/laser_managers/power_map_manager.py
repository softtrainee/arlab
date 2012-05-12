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
from traits.api import  Instance, Event, Property, \
    DelegatesTo, Str, Enum, Bool, Any, Float, Int, List
from traitsui.api import View, Item, HGroup, VGroup, \
    TableEditor, InstanceEditor, Handler
from traitsui.table_column import ObjectColumn

import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#import numpy as np
#============= local library imports  ==========================
from src.managers.manager import Manager
#from src.scripts.laser.power_map_script import PowerMapScript
#from src.canvas.canvas2D.raster_canvas import RasterCanvas
from threading import Thread

from src.lasers.laser_managers.power_mapping import PowerMapping
from src.helpers.paths import hidden_dir, co2laser_db
from pyface.timer.do_later import do_later
#from src.helpers.datetime_tools import get_datetime
from src.database.adapters.power_map_adapter import PowerMapAdapter

#from enable.component_editor import ComponentEditor
#class PowerMapStep(HasTraits):
#    beam_diameter = Float
#    padding = Float
#    step_length = Float
#    power = Float
#class PowerMapHandler(Handler):
#    def close(self, info, ok):
#        info.object.script.kill_script()
#        return True



class PowerMapManager(Manager):

#    script = Instance(PowerMapScript)
#    steps = DelegatesTo('script')
#    file_name = Str
#    save = Button
#    load = Button
    start_button = Event
    start_label = Property(depends_on='_alive')
    kind = Enum('normal', 'fast')

    _alive = Bool(False)
#    canvas = Instance(RasterCanvas)

    laser_manager = Any
    mappings = List
    database = Any

    application = DelegatesTo('laser_manager')
#    power_mapping = Instance(PowerMapping)
#    beam_diameter = Float(1)
#    request_power = Float(1)
#    padding = Int(1)
#    step_length = Float(0.25)
#    center_x = Float(0)
#    center_y = Float(0)

    def _get_start_label(self):
        return 'Stop' if self._alive else 'Start'

#    def _file_name_changed(self):
#
#        root, tail = os.path.split(self.file_name)
#        self.script.source_dir = root
#        self.script.file_name = tail
#        self.title = tail
#        self.script.load_steps()
#
    def close(self, is_ok):
        if is_ok:
            self._dump_power_maps()
        return is_ok

    def _dump_power_maps(self):
        p = os.path.join(hidden_dir, 'power_maps')
        with open(p, 'wb') as f:
            pickle.dump(self.mappings, f)

    def _load_power_maps(self):
        p = os.path.join(hidden_dir, 'power_maps')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    pmc = pickle.load(f)
                except Exception:
                    pmc = [PowerMapping()]
        else:
            pmc = [PowerMapping()]

        for pmi in pmc:
            pmi.name = 'PowerMap'
#            pmi.laser_manager = self.laser_manager
            pmi.parent = self

        return pmc

    def isAlive(self):
        return self._alive

    def _start_button_fired(self):
        if self.isAlive():
            self._alive = False
            self.end(user_cancel=True)
        else:
            self._alive = True
            self.execute()

    def kill(self):
        #suppress killing
        pass

    def end(self, user_cancel=False):
        lm = self.laser_manager
        lm.disable_laser()

    def _mappings_default(self):
        return self._load_power_maps()

    def execute(self):
        t = Thread(name='power_map.execute',
                   target=self._execute_)
        t.start()

    def _open_power_map(self, pi):
        ui = pi.edit_traits()
        self.add_window(ui)

    def _execute_(self):
        x = 50
        y = 20
        for i, pi in enumerate(self.mappings):
            if not self.isAlive():
                break

            pi.display_name = '{}'.format(i + 1)
            pi.window_x = x + i * 10
            pi.window_y = y + i * 20

            do_later(self._open_power_map, pi)
#            do_later(pi.edit_traits)

            try:
                pi.center_x = self.laser_manager.stage_manager.x
                pi.center_y = self.laser_manager.stage_manager.y
            except AttributeError:
                self.warning('stage manager not intialized')

            pi._execute_()

        self.end()
        self._alive = False

##        

#        if not self.script.isAlive():
#            self.script.kind = self.kind
#
#            self.script.bootstrap()
#        else:
#            self.script.kill_script(user_cancel=True)
#
#    def new_script(self):
#
#        root, name = os.path.split(self.file_name)
#        self.script = PowerMapScript(
#                              source_dir=root,
#                              file_name=name,
#                              manager=self.parent)
#        self.script.load_steps()
#
#    def _script_default(self):
#        return PowerMapScript()
#    def _canvas_default(self):
#        return RasterCanvas()
    def _database_default(self):
#        db = PowerMapAdapter(
#                             dbname='co2laserdb',
#                            password='Argon'
#                            )
        db = PowerMapAdapter(
                             dbname=co2laser_db,
                            kind='sqlite'
                            )
        db.connect()
        return db

    def _save_to_db(self, path):
        db = self.database
        p = db.add_powermap()
        db.add_path(p, path)
        db.commit()

    def row_factory(self):
        r = PowerMapping(parent=self)
        info = r.edit_traits(view='configure_view',
                             kind='modal')
        if info.result:
            self.mappings.append(r)

    def traits_view(self):
        cols = [
              ObjectColumn(name='beam_diameter'),
              ObjectColumn(name='padding'),
              ObjectColumn(name='step_length'),
              ObjectColumn(name='request_power', label='Power'),
#              ObjectColumn(name='est_duration', editable=False)

              ]
        editor = TableEditor(columns=cols,
                            show_toolbar=True,
                            deletable=True,
                            row_factory=self.row_factory)

        v = View(
                 VGroup(
                         HGroup(Item('kind', show_label=False),
                                self._button_factory('start_button', 'start_label', None, align='right')),

                         HGroup(

                                Item('mappings',
                                     editor=editor,
                                     width=0.32,
                                      show_label=False,),
#                                Item('script', width=0.68, show_label=False, style='custom', editor=InstanceEditor(view='canvas_view'))
#                                Item('power_mapping', show_label=False, style='custom'),
#                                Item('canvas', show_label=False,
#                                     editor=ComponentEditor())
                                )
                        ),
                title='Power Map Manager',
                handler=self.handler_klass,
                resizable=True,
#                width=890,
#                height=650
                )
        return v

#============= views ===================================
class DummyStageController(object):
    def get_xy(self):
        return 0, 0

    def at_velocity(self, k, ev):
        import time
        time.sleep(3)
        ev.set()
    def _set_single_axis_motion_parameters(self, *args, **kw):
        pass

class DummyStageManager(object):
    x = 0
    y = 0
    simulation = True
    def __init__(self):
        self.stage_controller = DummyStageController()

    def linear_move(self, *args, **kw):
        pass

class DummyLaserMan(object):
    simulation = True
    def __init__(self):
        self.stage_manager = DummyStageManager()

    def enable_laser(self):
        pass
    def disable_laser(self):
        pass
    def set_laser_power(self, a):
        pass

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('foo')
    dm = DummyLaserMan()
    m = PowerMapManager(laser_manager=dm)
    m.configure_traits()




#============= EOF ====================================
