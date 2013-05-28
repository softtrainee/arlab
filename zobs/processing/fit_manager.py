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
from traits.api import HasTraits, List, Str, Bool, on_trait_change, Button, Callable
from traitsui.api import View, Item, HGroup, Controller, InstanceEditor, ListEditor, \
    EnumEditor
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
#============= local library imports  ==========================
from src.viewable import Viewable
from src.constants import FIT_TYPES
# from src.ui.bound_enum_editor import BoundEnumEditor
import os
from src.paths import paths

class Fit(HasTraits):
    name = Str
    names = List
    fit = Str
    use = Bool(True)
    filter_str = Str
    do_binding = Callable(transient=True)
    add_fit = Button('+')
    delete_fit = Button('-')
    deletable = Bool(True)
    def traits_view(self):
        v = View(HGroup(
                        Item('use', show_label=False),
                        HGroup(Item('name',
                                    editor=EnumEditor(name='names'),
                                    show_label=False),
#                               Item('fit', editor=BoundEnumEditor(values=FIT_TYPES,
#                                                                  do_binding=self.do_binding
#                                                                  ),
                               Item('fit', editor=EnumEditor(values=FIT_TYPES,
#                                                                  do_binding=self.do_binding
                                                                  ),
                                    show_label=False),
                               Item('filter_str', show_label=False),
                               Item('add_fit', show_label=False),
                               Item('delete_fit', show_label=False, defined_when='deletable'),
                               enabled_when='use',
                            )
                        )
                 )
        return v

    def _fit_default(self):
        return FIT_TYPES[0]

    def _name_default(self):
        return self.names[0]

class FitManager(Viewable):
    fits = List
    save_changes = Bool(False)

    def traits_view(self):
        v = self.view_factory(
                            Item('fits', show_label=False, editor=ListEditor(
                                                                  mutable=False,
                                                                  editor=InstanceEditor(),
                                                                  style='custom'
                                                                  )),
                            Item('save_changes'),
                            buttons=['OK', 'Cancel'],
                            )
        return v


    @on_trait_change('fits:delete_fit')
    def _remove_fit(self, obj, name, old, new):
        self.fits.remove(obj)

    @on_trait_change('fits:add_fit')
    def _add_fit(self, obj, name, old, new):
        ind = self.fits.index(obj)
        fi = obj.clone_traits()
        fi.deletable = True
        self.fits.insert(ind + 1, fi)

    def do_fit_binding(self, v):
        for f in self.fits:
            f.fit = v

    def closed(self, is_ok):
        if is_ok:
            self.dump_fits()

    def get_fits(self):
        return [fi for fi in self.fits if fi.use]
#===============================================================================
# persistence
#===============================================================================
    def load_fits(self):
        p = os.path.join(paths.hidden_dir, 'fit_manager.fits')
        if os.path.isfile(p):
            try:
                with open(p, 'rb') as fp:
                    self.fits = pickle.load(fp)
            except (pickle.PickleError, EOFError):
                pass

        if not self.fits:
            self.fits = [Fit(deletable=False,
                             names=['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36'])]


        for fi in self.fits:
            fi.do_binding = self.do_fit_binding

    def dump_fits(self):

        p = os.path.join(paths.hidden_dir, 'fit_manager.fits')

        try:
            with open(p, 'wb') as fp:
                pickle.dump(self.fits, fp)
        except pickle.PickleError:
            pass


if __name__ == '__main__':
    r = FitManager()
    r.load_fits()
#    r.fits = [
#              Fit(name='H1', do_binding=r.do_fit_binding),
#              Fit(name='H2', do_binding=r.do_fit_binding),
#              Fit(name='H3', do_binding=r.do_fit_binding),
#
#              ]
    r.configure_traits()
#============= EOF =============================================
