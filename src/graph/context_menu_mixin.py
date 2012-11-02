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
from traits.api import HasTraits
from traitsui.menu import Menu, Action

#============= standard library imports ========================
#============= local library imports  ==========================

class ContextMenuMixin(HasTraits):
    def action_factory(self, name, func, **kw):
        '''
        '''
        return Action(name=name, on_perform=getattr(self, func),
                       **kw)

    def get_contextual_menu_save_actions(self):
        '''
        '''
        return [
               # ('Clipboard', '_render_to_clipboard', {}),
                ('PDF', 'save_pdf', {}),
               ('PNG', 'save_png', {})]

    def contextual_menu_contents(self):
        '''
        '''
        save_actions = []
        for n, f, kw in self.get_contextual_menu_save_actions():
            save_actions.append(self.action_factory(n, f, **kw))

        save_menu = Menu(
                       name='Save Figure',
                       *save_actions)

        if not self.crosshairs_enabled:
            crosshairs_action = self.action_factory('Show Crosshairs',
                           'show_crosshairs'
                           )
        else:
            crosshairs_action = self.action_factory('Hide Crosshairs',
                           'destroy_crosshairs')

        export_actions = [
                          self.action_factory('Window', 'export_data'),
                          self.action_factory('All', 'export_raw_data'),

                          ]

        export_menu = Menu(name='Export',
                         *export_actions)
        contents = [save_menu, crosshairs_action, export_menu]

        if self.editor_enabled:
            pa = self.action_factory('Show Plot Editor', 'show_plot_editor')
            pa.enabled = self.selected_plot is not None
            contents += [pa]
            contents += [self.action_factory('Show Graph Editor', 'show_graph_editor')]

        return contents

    def get_contextual_menu(self):
        '''
        '''
        menu = Menu(*self.contextual_menu_contents()
                         )
        return menu


class IsotopeContextMenuMixin(ContextMenuMixin):
    def set_status(self):
        pass
    def contextual_menu_contents(self):
        contents = super(IsotopeContextMenuMixin, self).contextual_menu_contents()

        contents.append(Menu(
                             self.action_factory('Omit', 'set_status'),
                             self.action_factory('Include', 'set_status'),
                             name='status'))
        return contents

class RegressionContextMenuMixin(ContextMenuMixin):
    def contextual_menu_contents(self):
        contents = super(RegressionContextMenuMixin, self).contextual_menu_contents()
        actions = [
                 ('linear', 'cm_linear'),
                 ('parabolic', 'cm_parabolic'),
                 ('cubic', 'cm_cubic'),
                 (u'average \u00b1SD', 'cm_average_std'),
                 (u'average \u00b1SEM', 'cm_average_sem')
                 ]
        menu = Menu(
                    *[self.action_factory(name, func) for name, func in actions],
                    name='Fit')

#        contents.append(Menu(
#                             self.action_factory('Omit', 'set_status'),
#                             self.action_factory('Include', 'set_status'),
#                             name=))
        contents.append(menu)
        return contents

#============= EOF =============================================
