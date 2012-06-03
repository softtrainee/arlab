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
from traits.api import HasTraits, List, Instance, Enum, String, Button, Any
from traitsui.api import View, Item, Group, HGroup, TableEditor, spring
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from summary_window import SummaryWindow
class RecallItem(HasTraits):
    '''
        G{classtree}
    '''
    dbitem = Any

class RecallWindow(HasTraits):
    '''
        G{classtree}
    '''
    items = List(RecallItem)
    database = Instance(DatabaseAdapter)
    table = Enum('Projects')
    comparator = Enum('=')
    search_key = String
    search = Button
    db_session = None
    selected = Any

    summary = Button
    def __init__(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        super(RecallWindow, self).__init__(*args, **kw)
        self.refresh()
        self.show_summary_window()

    def _search_fired(self):
        '''
        '''
        self.refresh()

    def build_columns(self):
        '''
        '''
        cols = []
        for klass, args in self.get_columns():
            cols.append(klass(**args))
        return cols
    def get_columns(self):
        '''
        '''
        return [(ObjectColumn, dict(name='name')),
                 (ObjectColumn, dict(name='project_id'))
                 ]
    def refresh(self):
        '''
        '''
        self.items = []
        self.query()

    def get_filter_clause(self):
        '''
        '''
        rargs = None, None
        if self.search_key:
            print self.table, self.comparator, self.search_key
            if self.table == 'Projects':
                rargs = 'get_projects', dict(name=self.search_key)

        return rargs

    def get_analyses(self):
        '''
        '''
        gfunc, filter = self.get_filter_clause()
        if gfunc is not None:
            func = getattr(self.database, gfunc)
            items, sess = func(filter=filter)
            if items is not None:
                items = items.samples
            return items, sess
        else:
            return None, None
    def query(self):
        '''
        '''
        db = self.database
        if db is not None:
            analyses, sess = self.get_analyses()
            print analyses
            self.db_session = sess
            if analyses is not None:
                for s in analyses:
                    attrs = [a for a in dir(s) if a[0] != '_' and a != 'metadata']
                    kw = dict(dbitem=s)
                    for a in attrs:
                        kw[a] = getattr(s, a)
                    self.items.append(RecallItem(**kw))
            if sess is not None:
                sess.close()

    def _summary_fired(self):
        '''
        '''
        self.show_summary_window()

    def show_summary_window(self):
        '''
        '''
        analysis, self.db_session = self.database.get_analyses(filter=dict(id=5),
                                                                sess=self.db_session)

        s = SummaryWindow(
                          item=analysis)
        s.edit_traits()
    def on_table_click(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        print args, kw
    def traits_view(self):
        '''
        '''
        sg = Group(HGroup(
                          Item('table'),
                          Item('comparator'),
                          Item('search_key'),
                          spring,
                          Item('search'),
                          show_labels=False
                        ),
                 show_border=True)
        editor = TableEditor(columns=self.build_columns(),
                           #show_toolbar = False
                           selection_mode='row',
                           editable=False,
                           selected='selected',
                           on_dclick=self.on_table_click
                           )
        v = View(Item('items', show_label=False,
                      editor=editor
                      ),
                Item('summary', show_label=False),
                sg,
                      width=300,
                      height=500,
                 resizable=True)
        return v
#============= views ===================================
#============= EOF ====================================
