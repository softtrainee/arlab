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
