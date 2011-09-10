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
'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import HasTraits, Event, Any, Str, Float, Bool, List, Enum
from traitsui.api import View, Item, HGroup, VGroup, TableEditor, ButtonEditor, EnumEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
#=============standard library imports ========================

#=============local library imports  ==========================
class Streams(HasTraits):
    '''
        G{classtree}
    '''
    parent = Any
    name = Str
    include = Bool(False)
    delay = Float(1.0)
    _type = Enum('scatter', 'line')

    #options=Enum('a','b','c')


class StreamLoader(HasTraits):
    '''
        G{classtree}
    '''
    streams = List
    save_data = Bool(True)
    default_path = Bool(True)
    '''
    '''
    save_type = Enum('txt', 'h5')

    show_hide = Event
    label = Str('Include All')
    state = Bool

    time_units = 1
    def _show_hide_fired(self):
        '''
        '''
        self.state = not self.state

        for c in self.streams:
            c.include = self.state

        self.label = 'Exclude All' if self.state else 'Include All'

    def add_stream(self, parent):
        '''
            @_type parent: C{str}
            @param parent:
        '''
        s = Streams(parent=parent, name=parent.name)
        self.streams.append(s)

    def traits_view(self):
        '''
        '''
        cols = [
              ObjectColumn(name='name'),
              CheckboxColumn(name='include'),
              ObjectColumn(name='delay'),
              ObjectColumn(name='_type')
              ]
        table_editor = TableEditor(columns=cols)
        v = View(VGroup(
               HGroup(
                      Item('save_data'),
                      Item('default_path', visible_when='save_data'),
                      Item('save_type', visible_when='save_data', show_label=False)
                      ),
               HGroup(Item('time_units', editor=EnumEditor(values={1:'seconds', 60:'minutes', 3600:'hours'})), springy=False),
               Item('streams', show_label=False, editor=table_editor, height=75),
               HGroup(
                     Item('show_hide', editor=ButtonEditor(label_value='label'),
                           show_label=False,
                           springy=False
                           )
                     )
               ),
               height=500,
               width=100,
               resizable=True,
               #title = 'Select Streams',
               buttons=['OK', 'Cancel'])
        return v
