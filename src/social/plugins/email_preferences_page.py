#from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import Str, Password
from traitsui.api import  View, Item, Group
from apptools.preferences.ui.api import PreferencesPage

#============= standard library imports ========================

#============= local library imports  ==========================

class EmailPreferencesPage(PreferencesPage):
    name='Email'
    preferences_path='pychron.email'
    smtp_host=Str
    username=Str
    password=Password
    def traits_view(self):
        return View('smtp_host',
                    'username',
                    'password'
                    )

#    def traits_view(self):
#        '''
#        '''
#        v = View(grp,
#                 hardware_grp
#                 )
#        return v
#============= views ===================================
#============= EOF ====================================
