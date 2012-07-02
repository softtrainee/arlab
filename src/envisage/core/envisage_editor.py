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
from pyface.workbench.api import Editor
#============= standard library imports ========================

#============= local library imports  ==========================
def _id_generator():
    '''
    '''
    n = 1
    while True:
        yield(n)
        n += 1
_id_generator = _id_generator()
class EnvisageEditor(Editor):
    '''
    '''
    id_name = Str('')
    view_name = Str('')
    def _name_default(self):
        '''
        '''
        if not self.obj.name:
            name = 'New %s %i' % (self.id_name, _id_generator.next())
        else:
            name = self.obj.name
        return name

    def create_control(self, parent):
        '''
        '''
        args = dict(parent=parent, kind='subpanel')
        if self.view_name:
            args['view'] = self.view_name
        ui = self.obj.edit_traits(**args)
        return ui.control

#============= views ===================================
#============= EOF ====================================
