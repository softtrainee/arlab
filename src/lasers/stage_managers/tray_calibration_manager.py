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
from traits.api import Any, on_trait_change, Float, Button, Enum, String, Property, Str
from traitsui.api import View, Item, HGroup, VGroup, spring
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.paths import hidden_dir
from src.canvas.canvas2D.laser_tray_canvas import LaserTrayCanvas
from src.canvas.canvas2D.markup.markup_items import CalibrationItem, \
    CalibrationObject
from threading import Thread

PICKLE_PATH = p = os.path.join(hidden_dir, '{}_stage_calibration')
PYCHRON_HELP = '''1. Drag red circle to desired center position
2. Drag white circle to define tray rotation
Hit Accept to finish, Cancel to cancel
'''
MASSSPEC_HELP = '''1. Locate center hole
2. Locate right hole
'''
PYCHRON_AUTO_HELP = '''1. Hit calibrate.
2. Sit back and relax
'''

class TrayCalibrationManager(Manager):
    '''
        calibration points need to be saved in data space        
    '''
    calibrate = Button
#    calibration_label = Property(depends_on = 'calibration_step')
    calibration_step = String('Calibrate')
    accept = Button
    edit = Button
    cancel = Button

    _prev_calibration = None
    x = Float
    y = Float
#    rotation = Property(Float(enter_set = True, auto_set = False), depends_on = '_rotation')
#    _rotation = Float(enter_set = True, auto_set = False)
    rotation = Float
    canvas = LaserTrayCanvas
    calibration_style = Enum('MassSpec', 'pychron-auto')
    calibration_help = Property(depends_on='_calibration_help')
#    _calibration_help = Str(PYCHRON_HELP)
    _calibration_help = Str(PYCHRON_AUTO_HELP)
    _calibrating = False
#    def _get_rotation(self):
#        return self._rotation

    def _pychron_auto_calibration(self):
        canvas = self.canvas
        canvas.new_calibration_item(self.x,
                        self.y, 0, kind=self.calibration_style)

        #use our machine vision manager to do calibration
        if self.parent is not None:
            mv = self.parent.machine_vision_manager
            if mv is not None:
                self._calibrating = True
                calibration_item = canvas.calibration_item
                mv.do_auto_calibration(calibration_item)
                if canvas.calibration_item:
                    self.rotation = canvas.calibration_item.get_rotation()
                    self.save_calibration()
                self._calibrating = False


    def _do_mass_spec_calibration(self, x, y):
        canvas = self.canvas
        if self.calibration_step == 'Calibrate':
                self._calibrating = True
                _calibration = canvas.new_calibration_item(0, 0, 0, kind=self.calibration_style)
                self.calibration_step = 'Locate Center'
        elif self.calibration_step == 'Locate Center':
            canvas.calibration_item.set_center(x, y)
            self.calibration_step = 'Locate Right'
            self.x = x
            self.y = y
        elif self.calibration_step == 'Locate Right':
            canvas.calibration_item.set_right(x, y)

            self.rotation = canvas.calibration_item.get_rotation()
            self.save_calibration()
            self.calibration_step = 'Calibrate'
            self._calibrating = False



    def load_calibration(self, stage_map=None):
        if stage_map is None:
            stage_map = self.parent.stage_map

        p = PICKLE_PATH.format(stage_map)
        if os.path.isfile(p):
            self.info('loading saved calibration {}'.format(p))
            with open(p, 'rb') as f:

                try:
                    calibration = pickle.load(f)
                    try:
                        style = calibration.style
                    except AttributeError:
                        style = 'MassSpec'

                    if style == 'MassSpec':
                        self._calibration_help = MASSSPEC_HELP
                    elif style == 'pychron-auto':
                        self._calibration_help = PYCHRON_AUTO_HELP
#                    else:
#                        self._calibration_help = PYCHRON_HELP

                    calibration.set_canvas(self.canvas)
#                    calibration.on_trait_change(self.update_xy,
#                                                 'center.[x,y]')
#                    calibration.on_trait_change(self.update_rotation,
#                                                 'line.data_rotation')

#                    if isinstance(calibration, CalibrationItem):
#                        self._calibration_help = MASSSPEC_HELP
#                        if isinstance(calibration, CalibrationObject):
#                            self._calibration_help = PYCHRON_HELP

                    self.canvas.calibration_item = calibration

                    self.x, self.y = calibration.get_center_position()
#                    self.y = calibration.center.y
#                    self.rotation = calibration.line.data_rotation
                    self.rotation = calibration.get_rotation()
#                    print self.x, self.y, self.rotation
                    return True
                except (AttributeError, pickle.UnpicklingError), e:
                    print e

    def save_calibration(self):

        #delete the corrections file
        self.parent._stage_map.clear_correction_file()
        stage_map_name = self.parent.stage_map
        ca = self.canvas.calibration_item
        if  ca is not None:
            ca.style = self.calibration_style
            p = PICKLE_PATH.format(stage_map_name)
            self.info('saving calibration {}'.format(p))
            with open(p, 'wb') as f:
                pickle.dump(ca, f)

    def isCalibrating(self):
        return self._calibrating


#============= views ===================================
    def traits_view(self):
        v = View(VGroup(
                        Item('calibration_style'),
                        self._button_factory('calibrate', 'calibration_step',),

                        HGroup(
                        #Item('calibrate', show_label = False),
                        spring,
                        Item('edit', show_label=False,
                             enabled_when='editable',
                              visible_when='calibration_style=="pychron"'),
                        Item('accept', show_label=False,
                              enabled_when='object.canvas.calibrate',
                              visible_when='calibration_style=="pychron"'),
                        Item('cancel', show_label=False,
                              enabled_when='object.canvas.calibrate',
                              visible_when='calibration_style in ["pychron","pychron-auto"]'),
                              )
                        ),

                 Item('x', format_str='%0.3f', style='readonly'),
                 Item('y', format_str='%0.3f', style='readonly'),
                 Item('rotation', format_str='%0.3f', style='readonly'),
                 VGroup(
                        Item('calibration_help', style='readonly',
                             show_label=False,
                             height=2,
#                             springy=True
                             ),
                        #springy=True
                        )

                )
        return v

    def _calibrate_fired(self):
        '''
            turns the markup calibration canvas on
            by setting canvas.calibrate= True
        '''

        x = self.parent.stage_controller.x
        y = self.parent.stage_controller.y
        self.rotation = 0
        canvas = self.canvas

        if self.calibration_style == 'MassSpec':
            self._do_mass_spec_calibration(x, y)
        elif self.calibration_style == 'pychron-auto':
            if not self._calibrating:
                canvas.calibrate = True
                t = Thread(target=self._pychron_auto_calibration)
                t.start()
            #make a new calibration item

#        else:
#
#            if canvas.calibration_item is not None:
#                #remember the previous calibration
#                self._prev_calibration = canvas.calibration_item
#
#            calibration = canvas.new_calibration_item(self.x, self.y, 0)
#            canvas.markupcontainer['calibration_indicator'] = calibration
#
#            calibration.on_trait_change(self.update_xy, 'center.[x,y]')
#            calibration.on_trait_change(self.update_rotation,
#                                         'line.data_rotation')
#
#            canvas.calibrate = True
        canvas.request_redraw()

    def _edit_fired(self):
        canvas = self.canvas
        canvas.markupcontainer['calibration_indicator'] = canvas.calibration_item
        canvas.calibrate = True
        canvas.request_redraw()

    def _cancel_fired(self):
        canvas = self.canvas
        #try to cancel the machine vision manager 
        mv = self.parent.machine_vision_manager
        if mv is not None:
            mv.cancel_calibration()

        canvas.calibration_item = self._prev_calibration
        self._accept_fired()

    def _accept_fired(self):
        canvas = self.canvas

        canvas.markupcontainer.pop('calibration_indicator')

        canvas.calibrate = False
        canvas.request_redraw()

        self.save_calibration()

    def _calibration_style_changed(self):
        if self.calibration_style == 'MassSpec':
            if 'calibration_indicator' in self.canvas.markupcontainer:
                self.canvas.markupcontainer.pop('calibration_indicator')

            self._calibration_help = MASSSPEC_HELP
        elif self.calibration_style == 'pychron-auto':
            pass
        if not self.load_calibration():
            if self.canvas.calibration_item is not None:
                x = self.canvas.calibration_item.cx
                y = self.canvas.calibration_item.cy
                rotation = self.canvsas.calibration_item.get_rotation()
                self.canvas.new_calibration_item(x, y, rotation)

#        else:
#            if self.calibration_style == 'pychron-auto':
#                self._calibration_help = PYCHRON_AUTO_HELP
#            else:
#                self._calibration_help = PYCHRON_HELP
#
#            self.load_calibration()


    #    @on_trait_change('parent:stage_controller:[x,y]')
#    def update_stage_pos(self, obj, name, old, new):
#        setattr(self, name, new)

#    @on_trait_change('canvas:calibration_item:center:[x,y]')
#    def update_xy(self, obj, name, old, new):
#        if isinstance(new, float):
#            setattr(self, name, new)

    @on_trait_change('canvas:calibration_item:line:data_rotation')
    def update_rotation(self, obj, name, old, new):
        if isinstance(new, float):
            self.rotation = new

    def _get_calibration_help(self):
        return self._calibration_help

    def _get_calibration_label(self):
        return self.calibration_step
#============= EOF ====================================

