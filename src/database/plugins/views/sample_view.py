#============= enthought library imports =======================
from traits.api import Str, List, Property
from traitsui.api import View, Item, \
    EnumEditor
#============= standard library imports ========================

#============= local library imports  ==========================
from database_table_view import DatabaseTableView
from database_item import DatabaseItem
class Sample(DatabaseItem):
    '''
    '''
    name = Str
    id = Str
    project = Str

    _project_id = Property

    projects = Property
    _projects = List

    irradiation = Str
    _irradiation_id = Property

    irradiations = Property
    _irradiations = List


    def _get_projects(self):
        '''
        '''
        return self.get_items('projects')

    def _get_irradiations(self):
        '''
        '''
        return self.get_items('irradiations')

    def _get__irradiation_id(self):
        '''
        '''
        return self.get_id('irradiations')

    def _get__project_id(self):
        '''
        '''
        return self.get_id('projects')

    def traits_view(self):
        '''
        '''

        v = View(Item('name'),
                       Item('project', editor = EnumEditor(values = self.projects)),
                       Item('irradiation', editor = EnumEditor(values = self.irradiations)),
                       title = 'New Sample',

                       buttons = ['OK', 'Cancel']
                )
        return v

class SampleView(DatabaseTableView):
    '''
        G{classtree}
    '''

    klass = Sample
    id = 'sample'

    def get_table_editor(self):
        '''
        '''
        kw = dict(columns = self.get_table_columns(),
                  show_toolbar = True,
                  selection_mode = 'row',
                  selected = 'selected',
                  row_factory = self.row_factory,
                  )
        return self._table_editor_factory(kw)

    def _pre_add(self, obj):
        def set_enum_lists(id):
            items, _sess = getattr(self.database, 'get_%s' % id)()
            setattr(obj, '_%s' % id, [(i.id, i.name) for i in items])

        if self.database.connected:
            for i in ['irradiations', 'projects']:
                set_enum_lists(i)

    def _add_row(self, item):
        '''
            
        '''
        print 'addd', item._project_id, item._irradiation_id

        iid = item._irradiation_id
        pid = item._project_id

        if iid is None:
            iid = item._irradiations[0][0]

        if pid is None:
            pid = item._projects[0][0]

        dbsample, sess = self.database.add_sample(
                                                  dict(name = item.name),
                                                  dbproject = pid,
                                                  dbirradiation = iid
                                                  )
        if dbsample:
            sess.commit()
            item.id = str(dbsample.id)
            sess.close()
            return True



#============= views ===================================
#============= EOF ====================================
