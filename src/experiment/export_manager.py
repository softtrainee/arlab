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
from traits.api import Instance
from traitsui.api import View
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.export.exporter import MassSpecExporter
from src.experiment.export.export_spec import ExportSpec
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.experiment.identifier import convert_special_name
from src.experiment.automated_run import assemble_script_blob
from src.processing.search.selector_manager import SelectorManager

class ExportManager(IsotopeDatabaseManager):
    selector_manager = Instance(SelectorManager)
    destination = None
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

    def _export(self, uuid):
        from src.database.records.isotope_record import IsotopeRecord
        src = self.db

        # get a dbrecord for this analysis
        dbrecord = src.get_analysis_uuid(uuid)

        # make an IsotopeRecord for convenient attribute retrieval
        record = IsotopeRecord(_dbrecord=dbrecord)
        record.load_isotopes()
        spec = self._make_spec(record)

        # use an Exporter to export spec to dest
        exp = MassSpecExporter()

#        dest = self.destination
        dest = dict(username='root', password='Argon', host='localhost',
                  name='massspecdata_import'
                  )

        dest = '/Users/ross/Sandbox/exporttest.xml'
        exp.export(spec, dest)


    def _test_fired(self):

#        d = self.selector_manager
#        if self.db.connect():
#            info = d.edit_traits(kind='livemodal')
#            if info.result:
#                for si in d.selected_records:
#                    self.info('exporting {} {}'.format(si.record_id, si.uuid))
#                    self._export(si.uuid)
        self._export('220bffbe-c37d-4ff1-8128-3f329233fa2e')

    def traits_view(self):
        v = View('test')
        return v

    def _selector_manager_default(self):
        db = self.db
        d = SelectorManager(db=db)
        return d

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
