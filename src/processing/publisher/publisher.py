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
from traits.api import HasTraits, List, Instance, Button, Any, Enum, on_trait_change, \
    Property, cached_property, Dict
from traitsui.api import View, Item, Controller, UItem, spring, HGroup, \
    VGroup, SetEditor
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.processing.publisher.loaded_table import LoadedTableController
from src.processing.publisher.selected_table import SelectedTableController
from src.processing.publisher.table_model import LoadedTable, SelectedTable
from pyface.action.menu_manager import MenuManager
from traitsui.menu import Action


class Publisher(Loggable):
    loaded_table = Instance(LoadedTableController)
    selected_table = Instance(SelectedTableController)
    append_button = Button('Append')
    replace_button = Button('Replace')

    _selected = None

    @on_trait_change('loaded_table:model:groups')
    def _analyses_handler(self, new):
        self.selected_table.model.groups = [gi.clone_traits() for gi in self.loaded_table.model.groups]

    @on_trait_change('loaded_table:model:groups:selected')
    def _selected_row_handler(self, new):
#        print new
        self._selected = new


    @on_trait_change('loaded_table:selected')
    def _selected_page_handler(self, new):
        idx = self.loaded_table.model.groups.index(new)
        self.selected_table.selected = self.selected_table.model.groups[idx]

    @on_trait_change('selected_table:selected')
    def _selected_page_handler2(self, new):
        idx = self.selected_table.model.groups.index(new)
        self.loaded_table.selected = self.loaded_table.model.groups[idx]

#    def _append_button_fired(self):
#        if self.loaded_table.selected:
#            self.selected_table.model.analyses.extend(self.loaded_table.selected)
#
#    def _replace_button_fired(self):
#        if self.loaded_table.selected:
#            self.selected_table.model.analyses = self.loaded_table.selected

    def _loaded_table_default(self):
        return LoadedTableController(LoadedTable())

    def _selected_table_default(self):
        return SelectedTableController(SelectedTable())

    def traits_view(self):
        v = View(
                 HGroup(UItem('loaded_table', style='custom'),
                        VGroup(spring,
                               UItem('append_button'),
                               UItem('replace_button'),
                               spring
                               ),
                        UItem('selected_table', style='custom')
                        ),
                 resizable=True,
                 height=700,
                 width=800,
                 x=100,
                 y=100,
                 title='Publisher'
                 )
        return v



if __name__ == '__main__':
    out = '/Users/ross/Sandbox/publish.pdf'

    pub = Publisher()
    pub.configure_traits()
#    pi = pub.writer(out, kind='pdf')

#    ans = [DummyAnalysis(labnumber='4000',
#                         aliquot=i)
#                         for i in range(5)]
#    ta = pi.add_ideogram_table(ans, add_title=True, add_header=True)
#    ans = [DummyAnalysis(labnumber='5000',
#                         aliquot=i
#                         ) for i in range(5)]
#
#    pi.add_ideogram_table(ans,
#                          widths=ta.get_widths(),
#                          add_header=True)
# #    ans = [DummyAnalysis(record_id='6000-{:02n}'.format(i)) for i in range(5)]
# #    pi.add_ideogram_table(ans)
# #    ans = [DummyAnalysis(record_id='7000-{:02n}'.format(i)) for i in range(5)]
# #    pi.add_ideogram_table(ans)
#    pi.publish()
#
#    import webbrowser
#    webbrowser.open('file://{}'.format(out))



#============= EOF =============================================
