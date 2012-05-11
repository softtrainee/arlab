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
                    Item('site_name', label='Name'),
                    Item('site_location', label='Location')
                    ))
        return v
#============= views ===================================
#============= EOF ====================================
