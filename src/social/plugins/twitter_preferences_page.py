#from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import Str, Password
from traitsui.api import  View, Item, Group
from apptools.preferences.ui.api import PreferencesPage

#============= standard library imports ========================

#============= local library imports  ==========================

class TwitterPreferencesPage(PreferencesPage):
    name='Twitter'
    preferences_path='pychron.twitter'
    
#    def traits_view(self):
#        '''
#        '''
#        v = View(grp,
#                 hardware_grp
#                 )
#        return v
#============= views ===================================
#============= EOF ====================================
