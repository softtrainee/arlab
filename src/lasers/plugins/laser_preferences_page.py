#from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import Bool, Range, Enum, Color
from traitsui.api import  Item, Group

#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.plugins.manager_preferences_page import ManagerPreferencesPage

class LaserPreferencesPage(ManagerPreferencesPage):

    use_video = Bool(False)
    show_grids = Bool(True)
    show_laser_position = Bool(True)
    show_desired_position = Bool(True)
    show_map = Bool(False)

    crosshairs_kind = Enum(1, 2, 3, 4)
    crosshairs_color = Color('maroon')#Enum('red', 'green', 'blue', 'yellow', 'black')
    desired_position_color = Color('green')
    calibration_style = Enum('pychron', 'MassSpec')
    scaling = Range(1.0, 3.0, 1.0)
    close_after = Range(0, 60, 1)
    def get_additional_groups(self):
        grp = Group(
               Item('use_video'),
               Item('show_map'),
               Item('show_grids'),
               Item('show_laser_position'),
               Item('show_desired_position'),
               Item('desired_position_color', show_label = False, enabled_when = 'show_desired_position'),
               Item('crosshairs_kind', label = 'Crosshairs', enabled_when = 'show_laser_position'),
               Item('crosshairs_color', enabled_when = 'show_laser_position'),
               Item('calibration_style'),
               Item('scaling'),
               label = 'Stage',
               )
        grp2 = Group(Item('close_after'))
        return [grp, grp2]

#    def traits_view(self):
#        '''
#        '''
#        v = View(grp,
#                 hardware_grp
#                 )
#        return v
#============= views ===================================
#============= EOF ====================================
