#============= enthought library imports =======================
from traits.api import Instance, DelegatesTo, List, Property
from traitsui.api import View, Item
#============= standard library imports ========================
#import os
#============= local library imports  ==========================
from modeler import Modeler
from src.envisage.core.envisage_manager import EnvisageManager
from src.envisage.core.envisage_editor import EnvisageEditor

class MEditor(EnvisageEditor):
    '''
        G{classtree}
    '''
    id_name = 'Modeler'
    view_name = 'graph_view'

class ModelerManager(EnvisageManager):
    _modeler = Instance(Modeler)
    modeler = Property(depends_on = '_modeler')
    modelers = List(Modeler)
    editor_klass = MEditor

    selected_datum = DelegatesTo('modeler', prefix = 'selected')
    def _selected_changed(self, old, new):
        self._modeler = new



    def new_modeler(self):
        self.open_modeler(m = self._modeler_factory())

    def _get_modeler(self):
        return self._modeler

    def parse_autoupdate(self):
        self.modeler.parse_autoupdate()

    def open_run_configuration(self):
        self.modeler.open_run_configuration()

    def run_model(self):
        self.modeler.run_model()

    def open_default(self):
        self.open_modeler()

    def open_modeler(self, m = None):
        if m is None:
            m = self.modeler
        self.selected = m
        self.window.workbench.edit(m,
                                   kind = self.editor_klass,
                                   use_existing = False
                                   )

        self._modeler = m

    def save(self):
        path = self._file_dialog('save as')
        if path is not None:
            self.modeler.graph.save_png(path = path)

    def __modeler_default(self):
        return self._modeler_factory()

    def _modeler_factory(self):
        m = Modeler()
        m.refresh_graph()

        return m

    def data_select_view(self):
        return View(Item('_modeler', style = 'custom', show_label = False))
#============= views ===================================
#============= EOF ====================================
