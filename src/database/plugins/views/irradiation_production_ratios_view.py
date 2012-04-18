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
from traits.api import CFloat, Str, Property, List
from traitsui.api import View, Item, HGroup, VGroup, Label, spring, EnumEditor
from traitsui.table_column import ObjectColumn
#============= standard library imports ========================

#============= local library imports  ==========================
from database_table_view import DatabaseTableView
from database_item import DatabaseItem
class IrradiationProductionRatios(DatabaseItem):
    '''
    '''
    ca3637 = CFloat
    ca3837 = CFloat
    ca3937 = CFloat
    k3739 = CFloat
    k3839 = CFloat
    k4039 = CFloat
    cl3638 = CFloat
    cak = CFloat
    clk = CFloat

    ca3637er = CFloat
    ca3837er = CFloat
    ca3937er = CFloat
    k3739er = CFloat
    k3839er = CFloat
    k4039er = CFloat
    cl3638er = CFloat
    caker = CFloat
    clker = CFloat

    irradiation = Str
    _irradiation_id = Property

    irradiations = Property
    _irradiations = List

    def _get_irradiations(self):
        '''
        '''
        return self.get_items('irradiations')

    def _get__irradiation_id(self):
        '''
        '''
        return self.get_id('irradiations')

    def traits_view(self):

        view = View(#Item('name'),
                       Item('irradiation', editor=EnumEditor(values=self.irradiations)),
                       VGroup(

                              HGroup(spring, Label('Value'), spring, Label('Error'), spring),
                              HGroup(spring, Item('ca3637'), Item('ca3637er', show_label=False)),
                              HGroup(spring, Item('ca3837'), Item('ca3837er', show_label=False)),
                              HGroup(spring, Item('ca3937'), Item('ca3937er', show_label=False)),

                              HGroup(spring, Item('k3739'), Item('k3739er', show_label=False)),
                              HGroup(spring, Item('k3839'), Item('k3839er', show_label=False)),
                              HGroup(spring, Item('k4039'), Item('k4039er', show_label=False)),

                              HGroup(spring, Item('cl3638'), Item('cl3638er', show_label=False)),
                              HGroup(spring, Item('cak'), Item('caker', show_label=False)),
                              HGroup(spring, Item('clk'), Item('clker', show_label=False)),
                              show_border=True,
                              label='Production Ratios'
                              ),
                       title='New IrradiationProductionRatios',
                       buttons=['OK', 'Cancel'])
        return view

class IrradiationProductionRatiosView(DatabaseTableView):
    '''
    '''

    klass = IrradiationProductionRatios
    id = 'irradiation_production_ratios'

    def get_table_editor(self):
        '''
        '''
        kw = dict(columns=self.get_table_columns(),
                  show_toolbar=True,
                  selection_mode='row',
                  selected='selected',
                  row_factory=self.row_factory
                  )
        return self._table_editor_factory(kw)
    def get_table_columns(self):
        return [
                ObjectColumn(name='id', editable=False),
                ObjectColumn(name='ca3637', editable=False),
                ObjectColumn(name='ca3837', editable=False),

                ]
    def _pre_add(self, item):
        def set_enum_lists(id):
            items, _sess = getattr(self.database, 'get_{}'.format(id))()
            setattr(item, '_{}'.format(id), [(i.id, i.name) for i in items])

        if self.database.connected:
            for i in ['irradiations']:
                set_enum_lists(i)

    def _add_row(self, item):
        '''

        '''
        args = dict()
        for k in item.traits():
            if not k.startswith('trait') and not k in ['irradiations', 'irradiation', '_irradiations', '_irradiation_id']:
                args[k] = item.trait_get(k)[k]

        iid = item._irradiation_id
        if iid is None:
            iid = item._irradiations[0][0]
        dbirradiation, sess = self.database.add_irradiation_production_ratios(args,
                                                                             dbirradiation=iid
                                                                             )
        if dbirradiation:
            sess.commit()
            item.id = str(dbirradiation.id)
            sess.close()
            return True



#============= views ===================================
#============= EOF ====================================
