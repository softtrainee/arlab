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
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================

class UpdateToHeadAction(Action):
    '''
        G{classtree}
    '''
    description = 'Update Pychron to the head revision'
    name = 'Update to head'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        client = app.get_service('src.svn.svn_client.SVNClient')
        client.update_to_head()

#============= EOF ====================================
