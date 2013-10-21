# @PydevCodeAnalysisIgnore
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
from traitsui.api import View, Item, TreeEditor, TreeNode, HSplit
from traitsui.menu import Action
from apptools.preferences.ui.preferences_manager import PreferencesManager, \
    PreferencesManagerHandler
from apptools.preferences.ui.preferences_node import PreferencesNode
#============= standard library imports ========================
#============= local library imports  ==========================

class PychronPreferencesManager(PreferencesManager):
    def traits_view(self):
        """ Default traits view for this class. """

        help_action = Action(name='Info', action='preferences_help')

        buttons = ['OK', 'Cancel']

        if self.show_apply:
            buttons = ['Apply'] + buttons
        if self.show_help:
            buttons = [help_action] + buttons


        # A tree editor for preferences nodes.
        tree_editor = TreeEditor(
            nodes=[
                TreeNode(
                    node_for=[PreferencesNode],
                    auto_open=False,
                    children='children',
                    label='name',
                    rename=False,
                    copy=False,
                    delete=False,
                    insert=False,
                    menu=None,
                ),
            ],
            on_select=self._selection_changed,
            editable=False,
            hide_root=True,
            selected='selected_node',
            show_icons=False
        )

        view = View(
            HSplit(
                Item(
                    name='root',
                    editor=tree_editor,
                    show_label=False,
                    width=250,
                ),

                Item(
                    name='selected_page',
                    # editor     = WidgetEditor(),
                    show_label=False,
                    width=450,
                    style='custom',
                ),
            ),

            buttons=buttons,
            handler=PreferencesManagerHandler(model=self),
            resizable=True,
            title='Preferences',
            width=.3,
            height=.7,
            kind='modal'
        )
        self.selected_page = self.pages[0]
        return view
#============= EOF =============================================
