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
from traits.api import HasTraits, Instance, Enum, Property, \
    Str, File, Any, Button, Int, List
from traitsui.api import View, Item, InstanceEditor, UItem, ListStrEditor, \
    Group, HGroup
from pyface.file_dialog import FileDialog
from pyface.constant import OK
#============= standard library imports ========================
import time
#============= local library imports  ==========================
# from src.experiment.export.exporter import MassSpecExporter
from src.experiment.export.export_spec import ExportSpec
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.experiment.identifier import convert_special_name
from src.experiment.automated_run import assemble_script_blob
from src.processing.search.selector_manager import SelectorManager
from src.database.database_connection_spec import DBConnectionSpec
from src.progress_dialog import MProgressDialog

class MassSpecDestination(HasTraits):
    destination = Property
    dbconn_spec = Instance(DBConnectionSpec, ())
    def _get_destination(self):
        return self.dbconn_spec.make_connection_dict()

    def traits_view(self):
        return View(Item('dbconn_spec', show_label=False, style='custom'))

    @property
    def url(self):
        return self.dbconn_spec.make_url()

class XMLDestination(HasTraits):
    destination = Str('/Users/ross/Sandbox/exporttest2.xml')
    browse_button = Button('browse')
    def _browse_button_fired(self):
        dlg = FileDialog(action='save as')
        if dlg.open() == OK:
            self.destination = dlg.path
#    destination = File('/Users/ross/Sandbox/exporttest2.xml')
    def traits_view(self):
        return View(HGroup(UItem('destination', width=0.75),
                           UItem('browse_button', width=0.25)))
    @property
    def url(self):
        return self.destination
class ExportManager(IsotopeDatabaseManager):
    selector_manager = Instance(SelectorManager)
    kind = Enum('XML', 'MassSpec')
    destination = Any

    export_button = Button('Export')
    exported = List

#===============================================================================
# private
#===============================================================================
    def _export(self, records):
        from src.database.records.isotope_record import IsotopeRecord
        src = self.db

        dest = self.destination.destination

        self.info('starting {} export'.format(self.kind))
        if self.kind == 'MassSpec':
            from src.experiment.export.exporter import MassSpecExporter
            exp = MassSpecExporter(dest)

        else:
            from src.experiment.export.exporter import XMLExporter
            exp = XMLExporter(dest)

        n = len(records)
        pd = MProgressDialog(max=n + 1, size=(550, 15))
        pd.open()
        pd.center()

        # make an IsotopeRecord for convenient attribute retrieval
        record = IsotopeRecord()
        st = time.time()
        for i, rec in enumerate(records):
            self.info('adding {} {} to export queue'.format(rec.record_id, rec.uuid))
            pd.change_message('Adding {}/{} {}    {}'.format(i + 1, n, rec.record_id, rec.uuid))

            # reusing the record object is 45% faster than making a new one each iteration
            # get a dbrecord for this analysis
            record._dbrecord = src.get_analysis_uuid(rec.uuid)

            record.load_isotopes()
            spec = self._make_spec(record)
            exp.add(spec)
            self.exported.append('{:04n} {}'.format(i + 1, rec.record_id))
            pd.increment()

        pd.change_message('Exporting...')
        self.info('exporting to {}'.format(self.destination.url))
        exp.export()
        pd.increment()

        t = time.time() - st
        self.info('export complete. exported {} analyses in {:0.2f}s'.format(n, t))

    def _make_spec(self, rec):
        # make script text
        scripts = []
        kinds = []
        ext = rec.extraction
        if ext and ext.script:
            scripts.append((ext.script.name, ext.script.blob))
            kinds.append('extraction')
        meas = rec.measurement
        if meas and meas.script:
            scripts.append((meas.script.name, meas.script.blob))
            kinds.append('measurement')

        scriptname, scripttxt = assemble_script_blob(scripts, kinds)

        # make a new ExportSpec
        es = ExportSpec(rid=convert_special_name(rec.labnumber),
                        spectrometer='Pychron {}'.format(rec.mass_spectrometer.capitalize()),
                        runscript_name=scriptname,
                        runscript_text=scripttxt
                        )

        # load spec with values from rec
        es.load_record(rec)

        # load spec with other values from rec
        for k in rec.isotope_keys:
            iso = rec.isotopes[k]
            xs, ys = iso.xs, iso.ys
            sig = zip(xs, ys)

            bxs, bys = iso.baseline.xs, iso.baseline.ys
            base = zip(bxs, bys)
            es.signals.append(sig)
            es.baselines.append(base)
            es.detectors.append((iso.detector, iso.name))
            es.signal_intercepts.append(iso.uvalue)
            es.baseline_intercepts.append(iso.baseline.uvalue)
            es.signal_fits.append(iso.fit)
            es.baseline_fits.append('Average Y')
            es.blanks.append(iso.blank.uvalue)

        return es
#===============================================================================
# handlers
#===============================================================================
    def _kind_changed(self):
        if self.kind == 'MassSpec':
            klass = MassSpecDestination
        else:
            klass = XMLDestination
        self.destination = klass()

    def _export_button_fired(self):
        d = self.selector_manager
        if self.db.connect():
            info = d.edit_traits(kind='livemodal')
            if info.result:
                self._export(d.selected_records)
        else:
            self.warning_dialog('Not connected to a source database')

    def _test_fired(self):
        self._export('220bffbe-c37d-4ff1-8128-3f329233fa2e')

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(UItem('kind'),
                 UItem('destination',
                      editor=InstanceEditor(),
                      style='custom',),
                 Group(
                       UItem('exported',
                             editor=ListStrEditor(editable=False,
                                                  drag_move=True,
                                                  operations=[],
                                                  horizontal_lines=True),
                             ),
                       show_border=True,
                       label='Exported'
                       ),
                 UItem('export_button'),
                 height=500,
                 width=400,
                 resizable=True
                 )
        return v
#===============================================================================
# defaults
#===============================================================================
    def _selector_manager_default(self):
        db = self.db
        d = SelectorManager(db=db)
        return d
    def _destination_default(self):
        return XMLDestination()

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('em')

    em = ExportManager()
    em.db.kind = 'mysql'
    em.db.name = 'isotopedb_bt'
    em.db.host = 'localhost'
    em.db.username = 'root'
    em.db.password = 'Argon'
    em.db.connect()
    em.configure_traits()
#============= EOF =============================================
