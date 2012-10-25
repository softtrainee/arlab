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
from traits.api import HasTraits, Float, Str, Instance, Unicode, Property, Event
from traitsui.api import View, Item, HGroup, VGroup, CheckListEditor
from src.managers.manager import SaveableHandler, SaveableButtons
from traitsui.menu import Action
from src.database.adapters.isotope_adapter import IsotopeAdapter
from traits.trait_errors import TraitError
from src.loggable import Loggable
#============= standard library imports ========================
#============= local library imports  ==========================
class ProductionRatio(HasTraits):
    value = Float
    error = Float
    name = Unicode
    def traits_view(self):
        v = View(HGroup(Item('name', style='readonly'),
                      Item('value'),
                      Item('error'),
                      show_labels=False))
        return v

class ProductionRatioInput(Loggable):
    db = Instance(IsotopeAdapter)
    name = Str
    db_name = Property(depends_on='_db_name')
    _db_name = Str
    names = Property(depends_on='saved')
    saved = Event
    #K interferences
    k4039 = Instance(ProductionRatio, (), {'name':'K 40/39'})
    k3839 = Instance(ProductionRatio, (), {'name':'K 38/39'})
    k3739 = Instance(ProductionRatio, (), {'name':'K 37/39'})


#    #Ca interferences
    ca3937 = Instance(ProductionRatio, (), {'name':'Ca 39/37'})
    ca3837 = Instance(ProductionRatio, (), {'name':'Ca 38/37'})
    ca3637 = Instance(ProductionRatio, (), {'name':'Ca 36/37'})

#    #Cl interference
    cl3638 = Instance(ProductionRatio, (), {'name':'Cl 36/38'})

    def _get_names(self):
        db = self.db
        ns = [str(ni.name) for ni in db.get_irradiation_productions()]
        return ns

    def save(self):
        self.info('saving production ratio')
        db = self.db

        keys = [
                'k4039', 'k3839', 'k3739',
                'ca3937', 'ca3837', 'ca3637',
                'cl3638'
                ]
        ekeys = ['{}_err'.format(ki) for ki in keys]
        values = [getattr(self, ki).value for ki in keys]
        errors = [getattr(self, ki).error for ki in keys]

        params = dict(zip(map(str.capitalize, keys + ekeys), values + errors))
        ip = db.get_irradiation_production(self.name)
        if ip:
            for k, v in params.iteritems():
                setattr(ip, k, v)
        else:
            params['name'] = self.name
            db.add_irradiation_production(**params)


        db.commit()
        self.saved = True
        self._db_name = '{}'.format(self.name)
#        self.trait_set(_db_name='{}'.format(self.name), trait_change_notify=False)

    def _get_db_name(self):
        return self._db_name

    def _set_db_name(self, n):
        self._db_name = n

    def _name_changed(self):
        if self.name in self.names:
            self._db_name = '{}'.format(self.name)
#            print self.db_name
#            self._db_name = self.name.capitalize()

#            print self.db_name
#            d = lambda: setattr(self, 'db_name', self.name.capitalize())
#            from pyface.timer.do_later import do_later
#            do_later(d)
#            self.db_name = self.name

    def __db_name_changed(self):
        ip = self.db.get_irradiation_production(self.db_name)
        self.name = self._db_name
        try:
            self.k4039.value = ip.K4039
            self.k4039.error = ip.K4039_err
            self.k3839.value = ip.K3839
            self.k3839.error = ip.K3839_err
            self.k3739.value = ip.K3739
            self.k3739.error = ip.K3739_err

            self.ca3937.value = ip.Ca3937
            self.ca3937.error = ip.Ca3937_err
            self.ca3837.value = ip.Ca3837
            self.ca3837.error = ip.Ca3837_err
            self.ca3637.value = ip.Ca3637
            self.ca3637.error = ip.Ca3637_err

            self.cl3638.value = ip.Cl3638
            self.cl3638.error = ip.Cl3638_err
        except TraitError:
            pass

#    def save_as(self):
#        print 'asdfasd'

    def traits_view(self):
        def item(n):
            return Item(n, style='custom', show_label=False)
        kgrp = VGroup(item('k4039'),
                      item('k3839'),
                      item('k3739'),
                       label='K', show_border=True)
        cagrp = VGroup(
                       item('ca3937'),
                       item('ca3837'),
                       item('ca3637'),
                       label='Ca', show_border=True)
        clgrp = VGroup(
                       item('cl3638'),
                       label='Cl', show_border=True)
        v = View(
                 VGroup(
                     HGroup(Item('name'),
                            Item('db_name',
                                 show_label=False,
                                 editor=CheckListEditor(name='names'))
                            ),
                     VGroup(kgrp,
                            cagrp,
                            clgrp,
                            )
                        ),
                 width=300,
                 resizable=True,
                 buttons=[Action(name='Save', action='save',
                                enabled_when='object.save_enabled'),
                          'Cancel'
                          ],
                 handler=SaveableHandler,
                 title='Production Ratio Input'
                 )
        return v

#    def _db_default(self):
#        return IsotopeAdapter(name='isotopedb_dev_migrate')

if __name__ == '__main__':
    d = ProductionRatioInput()
    d.configure_traits()
#============= EOF =============================================
