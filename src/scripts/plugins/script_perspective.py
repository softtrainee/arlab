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
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class ScriptPerspective(Perspective):
    '''
        G{classtree}
    '''
    name = 'Script'
    show_editor_area = True

    contents = [
              PerspectiveItem(id='pychron.process_view'),
              PerspectiveItem(id='script.errors', position='bottom', relative_to='pychron.process_view'),
              ]
#============= views ===================================
#============= EOF ====================================
