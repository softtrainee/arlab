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
     Button, List, Any, Bool, Property, Event, cached_property, Int
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
from src.constants import NULL_STR, MINNA_BLUFF_IRRADIATIONS
from collections import namedtuple
import time
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
    readable_names = Property(depends_on='names, names[]')
    selected = Any
    text_selected = Str
    scroll_to_row = Int
    imported_names = List
    custom_label1 = Str('Imported')
    filter_str = Str(enter_set=True, auto_set=False)
    progress = Int

    include_analyses = Bool(False)
    include_blanks = Bool(False)
    include_airs = Bool(False)
    include_cocktails = Bool(False)
#    include_analyses = Bool(True)
#    include_blanks = Bool(True)
#    include_airs = Bool(True)
#    include_cocktails = Bool(True)
    include_list = List
    update_irradiations_needed = Event
    dry_run = Bool(True)

    def _do_import(self, selected, pd):
        func = getattr(self.importer, 'import_{}'.format(self.import_kind))
        st = time.time()
        for si, inc in selected:
            pd.change_message('Importing {} {}'.format(si, inc))
            pd.increment()
#            for i in range(10):
#                time.sleep(0.1)
#            r = False
            r = func(self.db,
                     si,
                     include_analyses=self.include_analyses,
                     include_blanks=self.include_blanks,
                     include_airs=self.include_airs,
                     include_cocktails=self.include_cocktails,
                     dry_run=self.dry_run,
                     include_list=inc
                     )
            if r:
                self.imported_names.append(r)
                pd.change_message('Imported {} {} successfully'.format(si, inc))
                pd.increment()
            else:
                pd.change_message('Import {} {} failed'.format(si, inc))
                pd.increment()

            self.db.flush()

        if self.imported_names:
            self.update_irradiations_needed = True

        self.info('====== Import Finished elapsed_time= {}s======'.format(int(time.time() - st)))
#        self.db.close()

    @cached_property
    def _get_readable_names(self):
        return [ni.name for ni in self.names]

    def _text_selected_changed(self):
        txt = self.text_selected
        if ',' in txt:
            txt = txt.split(',')
        elif ':' in txt:

            start, end = txt.split(':')
            shead, scnt = start.split('-')
            ntxt = []
            if not end:
                return

            for i in range(int(end) - int(scnt) + 1):
                ntxt.append('{}-{}'.format(shead, int(scnt) + i))

            txt = ntxt
        else:
            txt = [txt]

        def get_name(name):
            return next((ni for ni in self.names if ni.name == name), None)

        sel = []
        for ti in txt:
            name = get_name(ti)
            if name is not None:
                sel.append(name)
        if sel:
            self.selected = sel
            self.scroll_to_row = self.names.index(sel[0])


    def _filter_str_changed(self):
        func = getattr(self.importer, 'get_{}s'.format(self.import_kind))
        self.names = func(filter_str=self.filter_str)

    def _open_button_fired(self):
        p = self.open_file_dialog()
        if p:
            with open(p, 'r') as fp:
                rids = [records(ri.strip()) for ri in fp.read().split('\n')]
                self.names = rids

    _import_thread = None
    def _import_button_fired(self):
#        self.import_kind = 'irradiation'
        if self.import_kind != NULL_STR:
#            if self.import_kind == 'rid_list':
#                '''
#                    load the import list
#                '''
#                self.selected = self.names
#            else:
#                self.selected = [records('NM-216')]
            selected = None
            if self.selected:
                selected = [(si.name, tuple()) for si in self.selected]

#            selected = [
#                        ('NM-205', ['E', ]),
# #                        ('NM-205', ['F' ]),
# #                        ('NM-256', ['F', ])
#                        ]
#            selected = MINNA_BLUFF_IRRADIATIONS

            if selected:
#                if self._import_thread and self._import_thread.isRunning():
#                    return

                if self.db.connect():
                    # clear imported
                    self.imported_names = []
                    self.db.reset()

                    self.db.save_username = 'jake({})'.format(self.db.username)
                    self.info('====== Import Started  ======')
                    self.info('user name= {}'.format(self.db.save_username))
                    # get import func from importer

                    n = len(selected) * 2
                    pd = self.open_progress(n=n)
                    from src.ui.thread import Thread
#                    self._do_import(selected, pd)
                    t = Thread(target=self._do_import, args=(selected, pd))
                    t.start()
                    self._import_thread = t



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
