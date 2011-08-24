#============= enthought library imports =======================
from traits.api import Bool
from traitsui.api import View, Item
from apptools.preferences.ui.api import PreferencesPage

#============= standard library imports ========================

#============= local library imports  ==========================


class HardwarePreferencesPage(PreferencesPage):
    '''
        G{classtree}
    '''
    name = 'Hardware'
    preferences_path = 'pychron.hardware'
    enable_hardware_server = Bool

    auto_find_handle = Bool
    auto_write_handle = Bool
    def traits_view(self):
        '''
        '''
        v = View(
                 'enable_hardware_server',
                 'auto_find_handle',
                 Item('auto_write_handle', enabled_when = 'auto_find_handle')
                 )
        return v
#============= views ===================================
#============= EOF ====================================
