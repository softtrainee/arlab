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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.database_adapter import DatabaseAdapter
from src.database.orms.bakeout_orm import BakeoutTable, ControllerTable, BakeoutPathTable
from src.database.selectors.bakeout_selector import BakeoutDBSelector


class BakeoutAdapter(DatabaseAdapter):
    test_func = None
    selector_klass = BakeoutDBSelector

#==============================================================================
#    getters
#==============================================================================

    def get_bakeouts(self, join_table=None, filter_str=None):
        try:
            if isinstance(join_table, str):
                join_table = globals()[join_table]

            q = self._get_query(BakeoutTable, join_table=join_table,
                                 filter_str=filter_str)
            return q.all()
        except Exception, e:
            print e

#=============================================================================
#   adder
#=============================================================================
    def add_bakeout(self, commit=False, **kw):
        b = self._add_timestamped_item(BakeoutTable, commit, **kw)
        return b

    def add_controller(self, bakeout, commit=False, **kw):
        c = ControllerTable(**kw)
        bakeout.controllers.append(c)
        if commit:
            self.commit()
        return c

    def add_path(self, bakeout, path, commit=False, **kw):
        kw = self._get_path_keywords(path, kw)
        p = BakeoutPathTable(**kw)
        bakeout.path = p
        if commit:
            self.commit()
        return p


if __name__ == '__main__':
    db = BakeoutAdapter(dbname='bakeoutdb',
                            password='Argon')
    db.connect()

    dbs = BakeoutDBSelector(_db=db)
    dbs._execute_()
    dbs.configure_traits()
#    print db.get_bakeouts(join_table='ControllerTable',
#                    filter_str='ControllerTable.script="---"'
#                    )


#============= EOF =============================================
#    def get_analyses_path(self):
##        sess = self.get_session()
##        q = sess.query(Paths)
##        s = q.filter_by(name='analyses')
#        q = self._get_query(Paths, name='analyses')
#        p = q.one()
#        p = p.path
#        return p
#
#    def get_intercepts(self, analysis_id):
#        q = self._get_query(Intercepts, analysis_id=analysis_id)
#        return q.all()
#
#    def get_analysis_type(self, **kw):
#        q = self._get_query(AnalysisTypes, **kw)
#        return q.one()
#
#    def get_spectrometer(self, **kw):
#        q = self._get_query(Spectrometers, **kw)
#        return q.one()
#    def add_intercepts(self, **kw):
#        o = Intercepts(**kw)
#        self._add_item(o)
#
#    def add_analysis(self, atype=None, spectype=None, **kw):
#        if atype is not None:
#            a = self.get_analysis_type(name=atype)
#            kw['type_id'] = a._id
#
#        if spectype is not None:
#            s = self.get_spectrometer(name=spectype)
#            kw['spectrometer_id'] = s._id
#
#        o = Analyses(**kw)
#        self._add_item(o)
#        return o._id
