'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from traits.api import Str, List, Button
from traitsui.api import View, Item, TabularEditor, EnumEditor, \
    HGroup, VGroup, Group, spring

from src.database.core.db_selector import DBSelector, DBResult
from src.database.nmgrl_orm import AnalysesTable
from src.database.nmgrl_database_adapter import NMGRLDatabaseAdapter
from traitsui.tabular_adapter import TabularAdapter

class MassSpecDBResult(DBResult):
    rid = Str

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
            print self.parameter
            tablename, param = self.parameter.split('.')

            c = self._convert_comparator(self.comparator)
            results = db.get_results(tablename,
                                 **{param:(c, self.criteria)}
                                 )
            for i, r in enumerate(results):
                r = MassSpecDBResult(_db_result=r,
                                     rid=r.RID,
                                     ridt=i
                                     )
                self.results.append(r)




if __name__ == '__main__':
    m = MassSpecSelector(parameter='AnalysesTable.RID',
                         criteria='21351-01')

    m._db = db = NMGRLDatabaseAdapter(dbname='massspecdata_local')
    db.connect()
    m.configure_traits()
#======== EOF ================================
