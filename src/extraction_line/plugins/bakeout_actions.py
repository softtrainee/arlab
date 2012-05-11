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
from src.envisage.core.action_helper import open_manager

#============= standard library imports ========================

#============= local library imports  ==========================

class OpenBakeoutManagerAction(Action):
    def perform(self, event):
        '''
        '''

        bmanager = self.window.application.get_service('src.managers.bakeout_manager.BakeoutManager')
#        bmanager.load()
        bmanager.load_controllers()


        open_manager(bmanager)
#        manager = self.window.application.get_service('src.managers.extraction_line_manager.ExtractionLineManager')
#        manager.show_bakeout_manager(bmanager)
#============= EOF ====================================
