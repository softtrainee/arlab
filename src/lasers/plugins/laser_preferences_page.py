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
#from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import Bool, Range, Enum, Color, Tuple, Directory
from traitsui.api import  Item, Group, HGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.plugins.manager_preferences_page import ManagerPreferencesPage

class LaserPreferencesPage(ManagerPreferencesPage):

    use_video = Bool(False)
    record_lasing = Bool(False)
    show_grids = Bool(True)
    show_laser_position = Bool(True)
    show_desired_position = Bool(True)
    show_map = Bool(False)

    crosshairs_kind = Enum(1, 2, 3, 4)
    crosshairs_color = Color('maroon')
    desired_position_color = Color('green')
    calibration_style = Enum('pychron', 'MassSpec')
    scaling = Range(1.0, 2.0, 1)

    auto_center = Bool(False)
    crosshairs_offset = Tuple(0, 0)
    crosshairs_offset_color = Color('blue')

    record_patterning = Bool(False)
    show_patterning = Bool(True)
    video_directory=Directory
    
    def get_additional_groups(self):
        grp = Group(
               Group(Item('use_video'),
                     Item('auto_center', enabled_when='use_video'),
                     Item('record_lasing', label='Record Lasing', enabled_when='use_video'),
                     Item('video_directory', label='Save to', enabled_when='record_lasing'),
                      show_border=True, label='Video'),
               Item('show_map'),
               Item('show_grids'),
               Item('show_laser_position'),
               Item('show_desired_position'),
               Item('desired_position_color', show_label=False, enabled_when='show_desired_position'),
               Item('crosshairs_kind', label='Crosshairs', enabled_when='show_laser_position'),
               Item('crosshairs_color', enabled_when='show_laser_position'),
               Item('crosshairs_offset'),
               Item('crosshairs_offset_color', show_label=False, enabled_when='crosshairs_offset!=(0,0)'),
               Item('calibration_style'),
               Item('scaling'),
               label='Stage',
               )
        patgrp = Group(Item('record_patterning'),
                       Item('show_patterning'), label='Pattern')

        return [grp, patgrp]
#============= EOF ====================================
