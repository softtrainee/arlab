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
from traits.api import Bool, Range, Enum, Color, Tuple, Directory, Float, Int
from traitsui.api import  Item, Group, HGroup, VGroup, Tabbed

#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.plugins.manager_preferences_page import ManagerPreferencesPage


class LaserPreferencesPage(ManagerPreferencesPage):

    use_video = Bool(False)
    video_identifier = Enum(1, 2)
    use_video_server = Bool(False)
    video_server_port = Int(1084)

    show_grids = Bool(True)
    show_laser_position = Bool(True)
    show_desired_position = Bool(True)
    show_map = Bool(False)

    crosshairs_kind = Enum(1, 2, 3, 4)
    crosshairs_color = Color('maroon')
    desired_position_color = Color('green')
    calibration_style = Enum('MassSpec', 'pychron-auto')
    scaling = Range(1.0, 2.0, 1)

    use_autocenter = Bool(True)
    crosshairs_offset = Tuple(0, 0)
    crosshairs_offset_color = Color('blue')

    show_patterning = Bool(True)
    video_directory = Directory
    use_video_archiver = Bool(True)
    video_archive_months = Range(0, 12, 1)
    video_archive_hours = Range(0, 23, 0)
    video_archive_days = Range(0, 31, 7)

    recording_zoom = Range(0, 100.0, 0.0)

    record_patterning = Bool(False)
    record_brightness = Bool(True)
    record_lasing_video = Bool(False)
    record_lasing_power = Bool(False)

    use_calibrated_power = Bool(True)
    show_bounds_rect = Bool(True)

    def get_additional_groups(self):
        archivergrp = Group(Item('use_video_archiver'),
                            Item('video_archive_days',
                                  label='Archive after N. days',
                                  enabled_when='use_video_archiver',
                                  ),
                            Item('video_archive_hours',
                                  label='Archive after N. hours',
                                  enabled_when='use_video_archiver',
                                  ),
                             Item('video_archive_months',
                                  label='Delete after N. months',
                                  enabled_when='use_video_archiver',
                                  ),
                             show_border=True,
                             label='Archiver'
                           )
        recgrp = Group(Item('record_lasing_video', label='Record Lasing'),
                       Item('record_brightness',
                            label='Record Brightness Measure',
                            ),
                       Item('video_directory', label='Save to',
                            enabled_when='record_lasing_video_video'),
                       Item('recording_zoom', enabled_when='record_lasing_video'),
                       show_border=True,
                       label='Record'
                     )
        vservergrp = VGroup(Item('use_video_server', label='Use Server'),
                                Item('video_server_port', label='Port',
                                enabled_when='use_video_server'),
                                show_border=True,
                                label='Server'
                                )
        videogrp = VGroup(Item('use_video'),
                     VGroup(
#                         Item('video_identifier', label='ID',
#                               enabled_when='use_video'),
                         Item('use_autocenter', label='Auto Center'),

                         recgrp,
                         archivergrp,
                         vservergrp,
                         enabled_when='use_video'
                         ),

                      label='Video')
        canvasgrp = VGroup(
               Item('show_bounds_rect'),
               Item('show_map'),
               Item('show_grids'),
               Item('show_laser_position'),
               Item('show_desired_position'),
               Item('desired_position_color', show_label=False,
                     enabled_when='show_desired_position'),
               Item('crosshairs_kind', label='Crosshairs',
                     enabled_when='show_laser_position'),
               Item('crosshairs_color', enabled_when='show_laser_position'),
               Item('crosshairs_offset'),
               Item('crosshairs_offset_color', show_label=False,
                    enabled_when='crosshairs_offset!=(0,0)'),
               Item('calibration_style'),
               Item('scaling'),
               label='Canvas',
               )

        patgrp = Group(Item('record_patterning'),
                       Item('show_patterning'), label='Pattern')
        powergrp = Group(
                        Item('record_lasing_power'),
                        Item('use_calibrated_power'),
                         label='Power')
        return [canvasgrp, videogrp, patgrp, powergrp]
#============= EOF ====================================
