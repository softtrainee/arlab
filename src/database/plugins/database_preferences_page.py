#============= enthought library imports =======================
from traits.api import Str, Password, Bool, Button
from traitsui.api import View, Item, VGroup
from apptools.preferences.ui.api import PreferencesPage

#============= standard library imports ========================

#============= local library imports  ==========================

class DatabasePreferencesPage(PreferencesPage):
    '''
        G{classtree}
    '''
    id = 'pychron.workbench.database.preferences_page'
    name = 'Database'
    preferences_path = 'pychron.database'
    dbname = Str
    user = Str
    password = Password
    host = Str
    use_db = Bool(False)

    test = Button
    def traits_view(self):
        '''
        '''
        v = View(VGroup(
                    Item('use_db'),
                    VGroup(
                    Item('dbname', label = 'Database Name'),
                    Item('host'),
                    Item('user'),
                    Item('password'),
                    show_border = True,
                    visible_when = 'use_db'
                    )
                    ))
        return v
#============= views ===================================
#============= EOF ====================================
