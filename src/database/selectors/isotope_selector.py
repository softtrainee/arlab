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
from traits.api import Int, Property
#from traits.api import HasTraits, Any, List, String, \
#    Float, Bool, Int, Instance, Property, Dict, Enum, on_trait_change, \
#    Str, Trait, cached_property
#from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor, \
#    InstanceEditor, ListEditor, EnumEditor, Label, Spring
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_selector import DatabaseSelector
#from src.database.core.base_db_result import DBResult
from src.database.orms.isotope_orm import meas_AnalysisTable, gen_LabTable, \
    gen_SampleTable, irrad_PositionTable, irrad_LevelTable, \
    irrad_IrradiationTable, gen_ProjectTable, meas_MeasurementTable, \
    gen_MassSpectrometerTable, gen_AnalysisTypeTable

#from src.graph.regression_graph import StackedRegressionTimeSeriesGraph, \
#    StackedRegressionGraph
#from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.database.core.base_results_adapter import BaseResultsAdapter
#from src.graph.graph import Graph

#from src.graph.stacked_graph import StackedGraph
from src.managers.data_managers.ftp_h5_data_manager import FTPH5DataManager
#from traits.trait_errors import TraitError
from src.managers.data_managers.h5_data_manager import H5DataManager
#from src.database.isotope_analysis.blanks_summary import BlanksSummary
#from src.experiment.identifier import convert_identifier, convert_labnumber, \
#    convert_shortname
#from src.database.isotope_analysis.fit_selector import FitSelector
from src.database.records.isotope_record import IsotopeRecord
from src.database.core.query import compile_query, IsotopeQuery

class IsotopeResultsAdapter(BaseResultsAdapter):
    columns = [
#               ('ID', 'rid'),
               ('Labnumber', 'labnumber'),
               ('Aliquot', 'aliquot'),
               ('Date', 'rundate'),
               ('Time', 'runtime'),
               ('Irradiation', 'irradiation'),
               ('Mass Spec.', 'mass_spectrometer'),
               ('Type', 'analysis_type')
#               ('Irradiation', 'irradiation_level')
               ]
    font = 'monospace'
#    rid_width = Int(50)
    labnumber_width = Int(90)
    aliquot_width = Int(90)
    rundate_width = Int(90)
    runtime_width = Int(90)
    aliquot_text = Property
    irradiation_text = Property
#    irradiation_level_text = Property

    def _get_irradiation_text(self):
        if self.item.irradiation:
            return '{}{} {}'.format(self.item.irradiation.name,
                                self.item.irradiation_level.name,
                                self.item.irradiation_position.position
                                )
        else:
            return ''

    def _get_aliquot_text(self, trait, item):
        a = self.item.aliquot
        s = self.item.step
        return '{}{}'.format(a, s)
#        return '1'
#    width = Int(50)

class IsotopeAnalysisSelector(DatabaseSelector):
    title = 'Recall Analyses'
    orm_path = 'src.database.orms.isotope_orm'

#    query_table = meas_AnalysisTable
    record_klass = IsotopeRecord
    query_klass = IsotopeQuery
    tabular_adapter = IsotopeResultsAdapter
#    multi_graphable = Bool(True)

#    def _load_hook(self):
#        jt = self._join_table_parameters
#        if jt:
#            self.join_table_parameter = str(jt[0])
#    def _selected_changed(self):
#        print self.selected
#    def set_data_manager(self, kind, **kw):
#        if kind == 'FTP':
#            dm = FTPH5DataManager(**kw)
#        else:
#            dm = H5DataManager(**kw)
#
#        self.data_manager = dm

    def _get_selector_records(self, queries=None, limit=None, **kw):
        sess = self.db.get_session()
        q = sess.query(meas_AnalysisTable)
        q = q.filter(meas_AnalysisTable.status != -1)

        mm = {'Labnumber':([gen_LabTable], gen_LabTable.labnumber),
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
        if queries:
            q = self._assemble_query(q, queries, mm)

        q = q.order_by(meas_AnalysisTable.analysis_timestamp.desc())
#        q = q.order_by(meas_AnalysisTable.runtime.desc())

        if limit:
            q = q.limit(limit)
        q = q.from_self()
        q = q.order_by(meas_AnalysisTable.analysis_timestamp.asc())

        records = q.all()
#        records.reverse()

#        arguments = ['-1']
#        if queries:
#            arguments.extend((qi.criterion for qi in queries))

        return records, compile_query(q)
#        return records, q.statement, ', '.join(arguments)
#        return q.all()


#        return self._db.get_analyses(**kw)

#    def _get__join_table_parameters(self):
#        dv = self._db.get_devices()
#        return list(set([di.name for di in dv if di.name is not None]))



#        f = lambda x:[str(col)
#                           for col in x.__table__.columns]
#        params = f(b)
#        return list(params)
#        return

#============= EOF =============================================

