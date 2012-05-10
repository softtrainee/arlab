#'''
#Copyright 2011 Jake Ross
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#'''
##============= enthought library imports =======================
#from traits.api import HasTraits, List, Instance
#from traitsui.api import View, Item, Handler, \
#    TableEditor
#from traitsui.table_column import ObjectColumn
#
##============= standard library imports ========================
#
##============= local library imports  ==========================
##from src.database.pychron_database_adapter import PychronDatabaseAdapter
#class DatabaseTableHandler(Handler):
#    def init(self, info):
#        '''
#        '''
#        info.object.load()
#
#class DatabaseTableView(HasTraits):
#    '''
#    '''
#    items = List
#    database = Instance(PychronDatabaseAdapter)
#    klass = None
#    def traits_view(self):
#        '''
#        '''
#        table = Item('items', show_label=False,
#                     editor=self.get_table_editor())
#        v = View(table,
#                 handler=DatabaseTableHandler)
#        return v
#
#    def _table_editor_factory(self, kw):
#        '''
#        '''
#        return TableEditor(**kw)
#
#    def get_table_columns(self):
#        '''
#        '''
#        cols = [
#              ObjectColumn(name='id', editable=False),
#              ObjectColumn(name='name', editable=False),
#              ]
#        return cols
#
#    def row_factory(self):
#        '''
#        '''
#        if self.klass is not None:
#            item = self.klass()
#            self._pre_add(item)
#            info = item.edit_traits(kind='modal')
#            if info.result:
#                if self.database.connected:
#                    if self._add_row(item):
#                        self.items.append(item)
#
#    def _pre_add(self, item):
#        '''
#            
#            subclasses should override this method to load enumeditor lists
#        '''
#
#        pass
#
#    def _add_row(self, item):
#        '''
#        '''
#        pass
#
#
#    def load(self, sess=None, refresh=True):
#        '''
#
#        '''
#        self.items = []
#        if self.database.connected:
#            getter = getattr(self.database, 'get_{}s'.format(self.id))
#            items, sess = getter(sess=sess)
#
#            if self.klass is not None:
#                for i in items:
#                    nu = self.klass()
#                    for attr in dir(i):
#                        if attr[:1] != '_' and attr != 'metadata':
#                            nu.trait_set(**{attr:str(getattr(i, attr))})
#
#                    self.items.append(nu)
#
#            return sess
#
##============= views ===================================
##============= EOF ====================================
