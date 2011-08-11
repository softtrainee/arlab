#============= enthought library imports =======================
from traits.api import Str
from traitsui.api import View, Item, VGroup
from apptools.preferences.ui.api import PreferencesPage

#============= standard library imports ========================

#============= local library imports  ==========================

class SVNPreferencesPage(PreferencesPage):
    '''
        G{classtree}
    '''
    id = 'pychron.workbench.svn.preferences_page'
    name = 'SVN'
    preferences_path = 'pychron.svn'
    site_name = Str
    site_location = Str('http://')
    def traits_view(self):
        '''
        '''
        v = View(VGroup(
                    Item('site_name', label = 'Name'),
                    Item('site_location', label = 'Location')
                    ))
        return v
#============= views ===================================
#============= EOF ====================================
