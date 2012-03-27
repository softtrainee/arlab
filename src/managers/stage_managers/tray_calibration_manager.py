'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import on_trait_change, Float, Button, Enum, String, Property, Str
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

PICKLE_PATH = p = os.path.join(hidden_dir, '.stage_calibration')
PYCHRON_HELP = '''1. Drag red circle to desired center position
2. Drag white circle to define tray rotation
Hit Accept to finish, Cancel to cancel
'''
MASSSPEC_HELP = '''1. Locate center hole
2. Locate right hole
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
    calibration_style = Enum('MassSpec', 'pychron', 'MassSpec')
    calibration_help = Property(depends_on='_calibration_help')
#    _calibration_help = Str(PYCHRON_HELP)
    _calibration_help = Str(MASSSPEC_HELP)
    _calibrating = False
#    def _get_rotation(self):
#        return self._rotation

    def isCalibrating(self):
        return self._calibrating

    def _cancel_fired(self):
        canvas = self.canvas
        canvas.calibration_item = self._prev_calibration
        self._accept_fired()

    def _accept_fired(self):
        canvas = self.canvas

        canvas.markupcontainer.pop('calibration_indicator')

        canvas.calibrate = False
        canvas.request_redraw()

        self.save_calibration()

    def _edit_fired(self):
        canvas = self.canvas
        canvas.markupcontainer['calibration_indicator'] = canvas.calibration_item
        canvas.calibrate = True
        canvas.request_redraw()

    def _calibrate_fired(self):
        '''
            turns the markup calibration canvas on
            by setting canvas.calibrate= True
        '''

        self.x = x = self.parent.stage_controller.x
        self.y = y = self.parent.stage_controller.y
        self.rotation = 0
        canvas = self.canvas

        if self.calibration_style == 'MassSpec':
            if self.calibration_step == 'Calibrate':
                self._calibrating = True
                calibration = canvas.new_calibration_item(self.x,
                        self.y, 0, kind=self.calibration_style)
                self.calibration_step = 'Locate Center'
            elif self.calibration_step == 'Locate Center':
                canvas.calibration_item.set_center(x, y)
                self.calibration_step = 'Locate Right'
            elif self.calibration_step == 'Locate Right':
                canvas.calibration_item.set_right(x, y)

                self.rotation = canvas.calibration_item.get_rotation()
                self.save_calibration()
                self.calibration_step = 'Calibrate'
                self._calibrating = False

        else:

            if canvas.calibration_item is not None:
                #remember the previous calibration
                self._prev_calibration = canvas.calibration_item

            calibration = canvas.new_calibration_item(self.x, self.y, 0)
            canvas.markupcontainer['calibration_indicator'] = calibration

            calibration.on_trait_change(self.update_xy, 'center.[x,y]')
            calibration.on_trait_change(self.update_rotation,
                                         'line.data_rotation')

            canvas.calibrate = True
        canvas.request_redraw()

    def load_calibration(self):
        if os.path.isfile(PICKLE_PATH):
            self.info('loading saved calibration {}'.format(PICKLE_PATH))
            with open(PICKLE_PATH, 'rb') as f:
                try:
                    calibration = pickle.load(f)
                    if isinstance(calibration, CalibrationItem):
                        self._calibration_help = MASSSPEC_HELP
                        if isinstance(calibration, CalibrationObject):
                            self._calibration_help = PYCHRON_HELP
                        calibration.set_canvas(self.canvas)
                        calibration.on_trait_change(self.update_xy,
                                                     'center.[x,y]')
                        calibration.on_trait_change(self.update_rotation,
                                                     'line.data_rotation')

                    self.canvas.calibration_item = calibration

                    self.x, self.y = calibration.get_center_position()
#                    self.y = calibration.center.y
#                    self.rotation = calibration.line.data_rotation
                    self.rotation = calibration.get_rotation()

                except (AttributeError, pickle.UnpicklingError), e:
                    print e

    def save_calibration(self):

        #delete the corrections file
        self.parent._stage_map.clear_correction_file()

        ca = self.canvas.calibration_item
        if  ca is not None:
            self.info('saving calibration')
            with open(PICKLE_PATH, 'wb') as f:
                pickle.dump(ca, f)

    @on_trait_change('parent:stage_controller:[x,y]')
    def update_stage_pos(self, obj, name, old, new):
        setattr(self, name, new)

    @on_trait_change('canvas:calibration_item:center:[x,y]')
    def update_xy(self, obj, name, old, new):
        if isinstance(new, float):
            setattr(self, name, new)

    @on_trait_change('canvas:calibration_item:line:data_rotation')
    def update_rotation(self, obj, name, old, new):
        if isinstance(new, float):
            self.rotation = new

    def _calibration_style_changed(self):
        if self.calibration_style == 'MassSpec':
            if 'calibration_indicator' in self.canvas.markupcontainer:
                self.canvas.markupcontainer.pop('calibration_indicator')

            self._calibration_help = MASSSPEC_HELP
        else:
            self._calibration_help = PYCHRON_HELP
            if self.canvas.calibration_item is not None:
                x = self.canvas.calibration_item.cx
                y = self.canvas.calibration_item.cy
                rotation = self.canvas.calibration_item.get_rotation()
                self.canvas.new_calibration_item(x, y, rotation)

    def _get_calibration_help(self):
        return self._calibration_help

    def _get_calibration_label(self):
        return self.calibration_step

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
                              visible_when='calibration_style=="pychron"'),
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
#============= EOF ====================================

