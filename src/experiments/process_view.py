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
from traits.api import HasTraits, Any, on_trait_change, String, Event, Property, Bool
from traitsui.api import View, Item, HGroup, spring, ButtonEditor

#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
class ProcessView(HasTraits):
    '''
        G{classtree}
    '''
    name = String
    execute = Event
    execute_label = Property(depends_on='alive')

    #experiment = Any
    #script = Any
    selected = Any
    dirty = Bool(False)
    alive = Bool(False)

    def _get_execute_label(self):
        return 'STOP' if self.alive else 'EXECUTE'

    def _execute_fired(self):
        '''
        '''

#        if self.experiment is not None:
#            obj = self.experiment
#
#        elif self.script is not None:
#            obj = self.script

        if self.selected:
            obj = self.selected
            if self.alive:
                obj.kill()
                self.alive = False
            else:
                if obj.execute():
                    self.alive = True
                    obj._script.on_trait_change(self.update_alive, '_alive')

    def update_alive(self, obj, name, old, new):
        '''
           handle the script death ie not alive
            
        '''
        self.alive = new

    def update_dirty(self, obj, name, old, new):
        self.dirty = new

    def selected_update(self, obj, name, old, new):
        if name == 'selected':
            self.selected = new
            if new is not None:
                self.name = new.name
                self.dirty = False
                new.on_trait_change(self.update_dirty, 'dirty')

    @on_trait_change('selected:name')
    def name_change(self, obj, name, old, new):
        '''
            @type obj: C{str}
            @param obj:

            @type name: C{str}
            @param name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        print obj, name, old, new
        if new is not None:
            self.name = new

    def traits_view(self):
        '''
        '''
        return View(Item('name'),
                    HGroup(
                           Item('execute',
                                editor=ButtonEditor(label_value='execute_label'),
                                       #enabled_when = 'experiment or script',
                                       enabled_when='not dirty',
                                       show_label=False)
                            ),
                            spring
                    )

#============= EOF ====================================
