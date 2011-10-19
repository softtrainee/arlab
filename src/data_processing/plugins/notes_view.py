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
from traits.api import HasTraits, Button, String
from traitsui.api import View, Item, HGroup, spring


#============= standard library imports ========================
import os
#============= local library imports  ==========================

#============= views ===================================
class NotesView(HasTraits):
    notes = String('')
    save = Button()
    def selected_update(self, obj, name, old, new):
        if new is not None:
            p = os.path.join(new.path, 'notes.txt')
            if os.path.isfile(p):
                f = open(p, 'r')
                self.notes = f.read()
                self.path = p
                f.close()


    def _save_fired(self):
        if self.path is not None:
            with open(self.path, 'w') as f:
                f.write(self.notes)

    def traits_view(self):
        v = View(HGroup(spring, Item('save', show_label=False)),
               Item('notes',
                     style='custom',
                     show_label=False))
        return v
