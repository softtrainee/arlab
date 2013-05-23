#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Enum, Instance, Str, Password, \
     Button, List, Any, Bool, Property, Event
# from traitsui.api import View, Item, VGroup, HGroup, spring, Group, TabularEditor
# from traitsui.tabular_adapter import TabularAdapter
# from apptools.preferences.preference_binding import bind_preference
# from src.processing.database_manager import DatabaseManager
# from src.database.adapters.massspec_database_adapter import MassSpecDatabaseAdapter
# from src.ui.custom_label_editor import CustomLabel
# from src.loggable import Loggable
# from src.database.database_connection_spec import DBConnectionSpec
from src.processing.importer.mass_spec_extractor import Extractor, \
    MassSpecExtractor
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.constants import NULL_STR
from collections import namedtuple
#============= standard library imports ========================
#============= local library imports  ==========================


records = namedtuple('Record', 'name')

class ImportManager(IsotopeDatabaseManager):
    data_source = Enum('MassSpec', 'File')
    importer = Instance(Extractor)
    import_kind = Enum('---', 'irradiation', 'rid_list')

    import_button = Button('Import')
    open_button = Button('Open')
    names = List
    selected = Any
    imported_names = List
    custom_label1 = Str('Imported')
    filter_str = Str(enter_set=True, auto_set=False)

    include_analyses = Bool(True)

    update_irradiations_needed = Event

    def _filter_str_changed(self):
        func = getattr(self.importer, 'get_{}s'.format(self.import_kind))
        self.names = func(filter_str=self.filter_str)

    def _open_button_fired(self):
        p = self.open_file_dialog()
        if p:
            with open(p, 'r') as fp:
                rids = [records(ri.strip()) for ri in fp.read().split('\n')]
                self.names = rids

    def _import_button_fired(self):
#        self.import_kind = 'irradiation'
        if self.import_kind != NULL_STR:
            if self.import_kind == 'rid_list':
                '''
                    load the import list
                '''
                self.selected = self.names
            else:
                self.selected = [records('NM-216')]

            if self.selected:
                if self.db.connect():
                    # clear imported
                    self.imported_names = []

                    # get import func from importer
                    func = getattr(self.importer, 'import_{}'.format(self.import_kind))
                    for si in self.selected:
                        r = func(self.db, si.name,
                                 self.include_analyses,
                                 include_list=['C', ]
                                 )
                        if r:
                            self.imported_names.append(r)

                    if self.imported_names:
                        self.update_irradiations_needed = True

    def _data_source_changed(self):
        if self.data_source == 'MassSpec':
            self.importer = MassSpecExtractor()
        else:
            self.importer = None

    def _import_kind_changed(self):
        try:
            func = getattr(self.importer, 'get_{}s'.format(self.import_kind))
            self.names = func()
        except AttributeError:
            pass

    def _importer_default(self):
        return MassSpecExtractor()

    def _data_source_default(self):
        return 'MassSpec'

#    def traits_view(self):
#        v = View(
#                 Item('data_source'),
#                 Item('importer', style='custom', show_label=False),
#                 Item('import_kind', show_label=False),
#                 Item('names', show_label=False, editor=TabularEditor(adapter=ImportNameAdapter(),
#                                                    editable=False,
#                                                    selected='selected',
#                                                    multi_select=True
#                                                    )),
#                 CustomLabel('custom_label1',
#                             color='blue',
#                             size=10),
#                 Item('imported_names', show_label=False, editor=TabularEditor(adapter=ImportedNameAdapter(),
#                                                    editable=False,
#                                                    )),
#
#                 HGroup(spring, Item('import_button', show_label=False)),
#                 width=500,
#                 height=700,
#                 title='Importer',
#                 resizable=True
#                 )
#        return v

if __name__ == '__main__':
    im = ImportManager()
    im.configure_traits()
#============= EOF =============================================
