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
#============= enthought library imports =======================
from traits.api import HasTraits, Str
from traitsui.api import View, Item
#============= standard library imports ========================

#============= local library imports  ==========================
from database_table_view import DatabaseTableView

class Irradiation(HasTraits):
    '''
        G{classtree}
    '''
    name = Str
    id = Str
    traits_view = View(Item('name'),
                       title = 'New Irradiation',
                       buttons = ['OK', 'Cancel'])

class IrradiationView(DatabaseTableView):
    '''
        G{classtree}
    '''

    klass = Irradiation
    id = 'irradiation'

    def get_table_editor(self):
        '''
        '''
        kw = dict(columns = self.get_table_columns(),
                  show_toolbar = True,
                  selection_mode = 'row',
                  selected = 'selected',
                  row_factory = self.row_factory
                  )
        return self._table_editor_factory(kw)

    def _add_row(self, item):
        '''
            @type item: C{str}
            @param item:
        '''
        dbirradiation, sess = self.database.add_irradiation(dict(name = item.name))
        if dbirradiation:
            sess.commit()
            item.id = str(dbirradiation.id)
            sess.close()
            return True



#============= views ===================================
#============= EOF ====================================
