#============= enthought library imports =======================
from traits.api import HasTraits, String
from traitsui.api import View, Item, HTMLEditor


#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
class HelpView(HasTraits):
    help_message = String('<body bgcolor = "#ffffcc" text = "#000000"></body>')

    def selected_update(self, obj, name, old, new):
        if hasattr(new, '_script'):
            doc = new._script.get_documentation()

            if doc is not None:
                self.help_message = str(doc)


    def traits_view(self):
        v = View(Item('help_message',
                    editor = HTMLEditor(),
                     show_label = False))
        return v