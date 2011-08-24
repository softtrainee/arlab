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
        v = View(HGroup(spring, Item('save', show_label = False)),
               Item('notes',
                     style = 'custom',
                     show_label = False))
        return v