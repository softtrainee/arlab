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
from traits.api import Property, List, Event, Instance, Button, cached_property
from traitsui.api import View, Item, EnumEditor, HGroup
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.viewable import Viewable
from src.processing.plotters.plotter_options import PlotterOptions, \
    IdeogramOptions
from src.paths import paths


class PlotterOptionsManager(Viewable):
    plotter_options_list = Property(List(PlotterOptions), depends_on='_plotter_options_list_dirty')
    _plotter_options_list_dirty = Event
    plotter_options = Instance(PlotterOptions)
    plotter_options_name = 'main'
    plotter_options_klass = PlotterOptions

    delete_options = Button('-')
    def close(self, ok):
        if ok:
            #dump the default plotter options
            p = os.path.join(paths.plotter_options_dir, '{}.default'.format(self.plotter_options_name))
            with open(p, 'w') as fp:
                obj = self.plotter_options.name
                pickle.dump(obj, fp)

            self.plotter_options.dump()
            self._plotter_options_list_dirty = True

#            self.plotter_options = next((pi for pi in self.plotter_options_list
#                                         if pi.name == self.plotter_options.name), None)

        return True

    def set_plotter_options(self, name):
        self.plotter_options = next((pi for pi in self.plotter_options_list
                                         if pi.name == name), None)

#===============================================================================
# handlers
#===============================================================================
    def _delete_options_fired(self):
        po = self.plotter_options
        if self.confirmation_dialog('Are you sure you want to delete {}'.format(po.name)):
            p = os.path.join(paths.plotter_options_dir, po.name)
            os.remove(p)
            self._plotter_options_list_dirty = True
            self.plotter_options = self.plotter_options_list[0]

    def traits_view(self):
        v = View(
                 HGroup(
                    Item('plotter_options', show_label=False,
                                   editor=EnumEditor(name='plotter_options_list')
                                ),
                    Item('delete_options',
                         enabled_when='object.plotter_options.name!="Default"',
                         show_label=False),
                        ),
                   Item('plotter_options', show_label=False,
                      style='custom'),
                 resizable=True,
#                               Item('edit_plotter_options', show_label=False),    
                 buttons=['OK', 'Cancel'],
                 handler=self.handler_klass,
                 title='Plot Options'
                )
        return v

    @cached_property
    def _get_plotter_options_list(self):
        r = paths.plotter_options_dir
        klass = self.plotter_options_klass
        ps = [klass(name='Default')]
        for n in os.listdir(r):
            if n.startswith('.') or n.endswith('.default') or n == 'Default':
                continue

            po = klass(name=n)
            ps.append(po)

        return ps

    def _plotter_options_default(self):
        p = os.path.join(paths.plotter_options_dir, '{}.default'.format(self.plotter_options_name))

        n = 'Default'
        if os.path.isfile(p):
            with open(p, 'r') as fp:
                try:
                    n = pickle.load(fp)
                except pickle.PickleError:
                    n = 'Default'

        po = next((pi for pi in self.plotter_options_list if pi.name == n), None)
        if not po:
            po = self.plotter_options_list[0]

        return po


class IdeogramOptionsManager(PlotterOptionsManager):
    plotter_options_klass = IdeogramOptions

#============= EOF =============================================
