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
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
#============= local library imports  ==========================

from src.database.selectors.db_selector import DBSelector

from src.database.adapters.massspec_database_adapter import MassSpecDatabaseAdapter
from src.database.selectors.base_db_result import RIDDBResult

class MassSpecDBResult(RIDDBResult):
    pass

class MassSpecDBResultsAdapter(TabularAdapter):
    columns = [('RunID', 'rid')
               #('ID', '_id'),
               #('Date', 'RunDateTime'),
               #('Time', 'runtime')
               ]

#    def get_bg_color(self, obj, trait, row, col):
#        print obj, trait, row, col
#        o = getattr(obj, trait)[row]

#        if 'group_marker' in o.rid:
#            return 'red'
#        else:
#            return 'white'
#
#    def get_text(self, obj, tr, row, column):
#
#        o = getattr(obj, tr)[row]
#        if 'group_marker' in o.rid:
#            return '----------'
#        else:
#            return getattr(o, self.columns[column][1])
#            return o

class MassSpecSelector(DBSelector):
    date_str = 'RunDateTime'
    tabular_adapter = MassSpecDBResultsAdapter

    def _get__parameters(self):
        return ['AnalysesTable.RID',
                'AnalysesTable.RunDateTime',
                ]

    def _search_(self):
        db = self._db
        if db is not None:
            tablename, param = self.parameter.split('.')

            c = self._convert_comparator(self.comparator)
            results = db.get_results(tablename,
                                 **{param:(c, self.criteria)}
                                 )
            for i, r in enumerate(results):
                r = MassSpecDBResult(_db_result=r,
                                     rid=r.RID,
#                                     ridt=i
                                     )
                self.results.append(r)


if __name__ == '__main__':
    m = MassSpecSelector(parameter='AnalysesTable.RID',
                         criteria='21351-01')

    m._db = db = MassSpecDatabaseAdapter(dbname='massspecdata_local')
    db.connect()
    m.configure_traits()
#============= EOF =============================================
