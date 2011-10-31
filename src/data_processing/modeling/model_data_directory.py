'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import HasTraits, Bool, Property, Str, Any


#============= standard library imports ========================
import os
#============= local library imports  ==========================

#============= views ===================================
class ModelDataDirectory(HasTraits):
    '''
    '''
    show = Bool
    bind = Bool
    name = Property(depends_on='path')
    path = Str
    id = 0
    modeler = Any
    def _get_name(self):
        '''
        '''
        return os.path.basename(self.path)

    def _show_changed(self):
        '''
        '''
        if self.modeler:
            self.modeler.graph.set_group_visiblity(self.show, gid=self.id)
            self.modeler.update_graph_title()


    def _bind_changed(self):
        '''
        '''
        if self.modeler:
            self.modeler.graph.set_group_binding(self.id, self.bind)

#============= EOF ====================================
