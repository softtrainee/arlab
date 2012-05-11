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



#from traits.api import HasTraits, Str, String, Button, List, Any, Long, Event, \
#    Date, Time, Instance, Dict, DelegatesTo, Property
#from traitsui.api import View, Item, TabularEditor, EnumEditor, \
#    HGroup, VGroup, Group, spring
#from traitsui.tabular_adapter import TabularAdapter
#
#from datetime import datetime, timedelta
from wx import GetDisplaySize
#import os

from .database_adapter import DatabaseAdapter
from src.database.orms.bakeout_orm import BakeoutTable, ControllerTable, PathTable
from src.database.selectors.bakeout_selector import BakeoutDBSelector
import os
#from src.helpers.datetime_tools import  get_date
#from src.loggable import Loggable
#from src.bakeout.bakeout_graph_viewer import BakeoutGraphViewer

DISPLAYSIZE = GetDisplaySize()


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

#    def _get_query(self, klass, join_table=None, filter_str=None, **clause):
#        sess = self.get_session()
#        q = sess.query(klass)
#
#        if join_table is not None:
#            q = q.join(join_table)
#
#        if filter_str:
#            q = q.filter(filter_str)
#        else:
#            q = q.filter_by(**clause)
#        return q

#    def open_selector(self):
#        s = BakeoutDBSelector(_db=self)
#        s._execute_()
#        s.edit_traits()

#=============================================================================
#   adder
#=============================================================================
    def add_bakeout(self, commit=False, **kw):
#        b = BakeoutTable(**kw)
        b = self._add_timestamped_item(BakeoutTable, commit)
#        self._add_item(b, commit)
        return b

    def add_controller(self, bakeout, commit=False, **kw):
        c = ControllerTable(**kw)
        bakeout.controllers.append(c)
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return c

    def add_path(self, bakeout, path, commit=False, **kw):
        kw = self._get_path_keywords(path, kw)
        p = PathTable(**kw)
        bakeout.path = p
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return p

#    def _add_item(self, obj, commit):
#        sess = self.get_session()
#        sess.add(obj)
#        if commit:
#            sess.commit()

#    def get_bakeouts2(self):
#        sess = self.get_session()
##        clause = dict(ControllerTable.script='---')
#        qcol = 'setpoint'
#        col = getattr(ControllerTable, qcol)
#        cond = 100
#        q = sess.query(BakeoutTable).join(ControllerTable).filter(col < cond)
#        print q.all()

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


#======== EOF ================================
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
