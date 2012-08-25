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
from traits.api import List
from envisage.api import Plugin
from pyface.workbench.api import TraitsUIView

#============= standard library imports ========================
#============= local library imports  ==========================
class CoreUIPlugin(Plugin):
    '''
    '''

    VIEWS = 'envisage.ui.workbench.views'
    PERSPECTIVES = 'envisage.ui.workbench.perspectives'
    ACTION_SETS = 'envisage.ui.workbench.action_sets'
    PREFERENCES_PAGES = 'envisage.ui.workbench.preferences_pages'

    preferences_pages = List(contributes_to=PREFERENCES_PAGES)
    perspectives = List(contributes_to=PERSPECTIVES)
    views = List(contributes_to=VIEWS)
    action_sets = List(contributes_to=ACTION_SETS)


    def check(self):
        '''
            a hook to see if the plugin is available 
            
            ie ImportError
        '''
        return True

    def traitsuiview_factory(self, args, kw):
        '''
        '''
        for k in kw:
            if k not in args:
                args[k] = kw[k]

        return TraitsUIView(**args)
#============= EOF ====================================
