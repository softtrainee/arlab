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
from traits.api import Int, Property, Str
# from traits.api import HasTraits, Any, List, String, \
#    Float, Bool, Int, Instance, Property, Dict, Enum, on_trait_change, \
#    Str, Trait, cached_property
# from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor, \
#    InstanceEditor, ListEditor, EnumEditor, Label, Spring
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_selector import DatabaseSelector
# from src.database.core.base_db_result import DBResult
from src.database.orms.isotope_orm import meas_AnalysisTable, gen_LabTable, \
    gen_SampleTable, irrad_PositionTable, irrad_LevelTable, \
    irrad_IrradiationTable, gen_ProjectTable, meas_MeasurementTable, \
    gen_MassSpectrometerTable, gen_AnalysisTypeTable

from src.database.core.base_results_adapter import BaseResultsAdapter
# from src.database.records.isotope_record import IsotopeRecord, IsotopeRecordView
from src.database.records.isotope_record import IsotopeRecordView
from src.database.core.query import  IsotopeQuery
from src.constants import NULL_STR, LINE_STR

class IsotopeResultsAdapter(BaseResultsAdapter):
    columns = [
#               ('ID', 'rid'),
               ('Labnumber', 'labnumber'),
               ('Aliquot', 'aliquot'),
               ('Analysis Time', 'timestamp'),
#               ('Time', 'runtime'),
               ('Irradiation', 'irradiation_info'),
               ('Mass Spec.', 'mass_spectrometer'),
               ('Type', 'analysis_type')
#               ('Irradiation', 'irradiation_level')
               ]
#     font = 'monospace 14'
#    rid_width = Int(50)
    labnumber_width = Int(90)
    aliquot_width = Int(50)
    rundate_width = Int(140)
#    runtime_width = Int(90)
#    aliquot_text = Property
#    irradiation_text = Property
#    irradiation_level_text = Property

#    def _get_irradiation_text(self):
#        if self.item.irradiation:
#            return '{}{} {}'.format(self.item.irradiation.name,
#                                self.item.irradiation_level.name,
#                                self.item.irradiation_position.position
#                                )
#        else:
#            return ''

#    def _get_aliquot_text(self, trait, item):
#        a = self.item.aliquot
#        s = self.item.step
#        return '{}{}'.format(a, s)
#        return '1'
#    width = Int(50)

class IsotopeAnalysisSelector(DatabaseSelector):
    title = 'Recall Analyses'
#    orm_path = 'src.database.orms.isotope_orm'

    query_table = meas_AnalysisTable
    record_view_klass = IsotopeRecordView
#     record_klass = IsotopeRecord
#    record_klass = DummyIsotopeRecord
    query_klass = IsotopeQuery
    tabular_adapter = IsotopeResultsAdapter
#    multi_graphable = Bool(True)

    lookup = {'Labnumber':([gen_LabTable], gen_LabTable.identifier),
              'Step':([], meas_AnalysisTable.step),
              'Aliquot':([], meas_AnalysisTable.aliquot),
              'Sample':([gen_LabTable, gen_SampleTable], gen_SampleTable.name),
              'Irradiation':([gen_LabTable,
                              irrad_PositionTable,
                              irrad_LevelTable,
                              irrad_IrradiationTable], irrad_IrradiationTable.name),
              'Irradiation Level':([gen_LabTable,
                              irrad_PositionTable,
                              irrad_LevelTable,
                              irrad_IrradiationTable], irrad_LevelTable.name),
              'Irradiation Position':([gen_LabTable,
                              irrad_PositionTable,
                              irrad_LevelTable,
                              irrad_IrradiationTable], irrad_PositionTable.position),
              'Run Date':([], meas_AnalysisTable.analysis_timestamp),
              'Project':([ gen_LabTable, gen_SampleTable, gen_ProjectTable, ], gen_ProjectTable.name),
              'Mass Spectrometer':([meas_MeasurementTable, gen_MassSpectrometerTable], gen_MassSpectrometerTable.name),
              'Analysis Type':([meas_MeasurementTable, gen_AnalysisTypeTable], gen_AnalysisTypeTable.name)

              }

    mass_spectrometer = Str('Spectrometer')
    mass_spectrometers = Property
    analysis_type = Str('Analysis Type')
    analysis_types = Property

    def _record_factory(self, idn):
        if isinstance(idn, meas_AnalysisTable):
            dbr = idn
        elif isinstance(idn, str):
            uuid = idn
        else:
            uuid = idn.uuid
            dbr = self.db.get_analysis(uuid, key='uuid')

        return self.record_klass(_dbrecord=dbr)

    def _get_selector_records(self, queries=None, limit=None, use_filters=True, **kw):
        with self.db.session_ctx() as sess:
#             sess = self.db.get_session()
            q = sess.query(meas_AnalysisTable)
            q = q.filter(meas_AnalysisTable.status != -1)
            if queries and use_filters:
                qs = self._build_filters()
                if qs:

                    queries = queries + qs
    #                queries.extend(qs)

            return self._get_records(q, queries, limit, timestamp='analysis_timestamp')

    def _get_mass_spectrometers(self):
        db = self.db
        mas = ['Spectrometer', LINE_STR]
        ms = db.get_mass_spectrometers()
        if ms:
            mas += [m.name for m in ms]
        return mas

    def _get_analysis_types(self):
        db = self.db
        ats = ['Analysis Type', LINE_STR]
        ai = db.get_analysis_types()
        if ai:
            ats += [aii.name.capitalize() for aii in ai]
        return ats

    def _analysis_type_changed(self):
        self._refresh_results()

    def _mass_spectrometer_changed(self):
        self._refresh_results()

    def _refresh_results(self):
        import inspect
        stack = inspect.stack()
        self.debug('update graph called by {}'.format(stack[1][3]))

#        qs = self._build_filters()
#        if qs:
#            qq = self.queries
        self.execute_query(load=False)

    def _build_filters(self):
        ma = self.mass_spectrometer
        an = self.analysis_type
        qs = []
#        if pr != NULL_STR:
#            q = selector.query_factory(parameter='Project', criterion=pr)
#            qs.append(q)
        if ma not in ('Spectrometer', LINE_STR):
            q = self.query_factory(parameter='Mass Spectrometer', criterion=ma)
            qs.append(q)

        if an not in ('Analysis Type', LINE_STR):
            q = self.query_factory(parameter='Analysis Type', criterion=an)
            qs.append(q)

        return qs
#============= EOF =============================================

