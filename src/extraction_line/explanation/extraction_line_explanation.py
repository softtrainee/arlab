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
#=============enthought library imports=======================
from traits.api import HasTraits, Any, Event, List, Bool, Property
from traitsui.api import View, Item, HGroup, VGroup, TableEditor, ButtonEditor, \
    Handler
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn


#=============standard library imports ========================

#=============local library imports  ==========================
#from filetools import parse_setupfile

from explanable_item import ExplanableTurbo


class ELEHandler(Handler):
    def init(self, info):
        if not info.initialized:
            info.object.selection_ok = True


class ExtractionLineExplanation(HasTraits):
    '''
    '''
    explanable_items = List
    #show_all = Button
    #hide_all = Button
    show_hide = Event
    label = Property(depends_on='identify')

    identify = Bool(False)
    #canvas = Any
    selected = Any
    selection_ok = False

    def on_selection(self, s):
        if self.selection_ok and s is not None:
            for ei in self.explanable_items:
                if ei != s:
                    ei.identify = False

            s.identify = not s.identify

    def _show_hide_fired(self):
        '''
        '''

        self.identify = not self.identify
        for c in self.explanable_items:
            c.identify = self.identify

        c.canvas.Refresh()

    def _get_label(self):
        return 'Hide All' if self.identify else 'Show All'

    def load_item(self, obj, name, old, new):
        if isinstance(new, list):
            for n in new:
                self.explanable_items.append(n)

    def load(self, l):
        '''
        '''
        #temp = None
        for v in l:
            self.explanable_items.append(v)
            #temp = v

#        for name, desc, id in [('An', 'Analytical', 'analytical_turbo'), ('Ro', 'Roughing', 'roughing_turbo')]:
#            t = ExplanableTurbo(name=name, description=desc, _id=id)
#            self.explanable_items.append(t)

    def traits_view(self):
        '''
        '''
        self.legend_editor = TableEditor(columns=[ObjectColumn(name='name',
                                                        editable=False),
           ObjectColumn(name='description', editable=False),
           ObjectColumn(name='state_property', editable=False, label='State'),
#                                           CheckboxColumn(name='identify'),
           ObjectColumn(name='lock_property', editable=False, label='Lock')
           ],
           selected='selected',
           on_select=self.on_selection
                            #editable = False,
                            )
        v = View(
               VGroup(HGroup(
                       Item('show_hide', editor=ButtonEditor(label_value='label'),
                           show_label=False,
                           springy=False)),

                      Item('explanable_items',
                           editor=self.legend_editor,
                           show_label=False,
                           #width=0.45
                           ),


                      ),
                 handler=ELEHandler
                #resizable = True,
                #scrollable = True,
                )
        return v
