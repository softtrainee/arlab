#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, String, List, Str, Float, Dict
from traitsui.api import View, Item, ListEditor

#============= standard library imports ========================
from datetime import datetime
#============= local library imports  ==========================
from src.helpers.color_generators import color8i_generator
from styled_text_display import StyledTextDisplay


def time_stamp_generator():
    '''
    '''

    while 1:
        yield datetime.now().isoformat(' ')

class MessagingDisplay(StyledTextDisplay):
    '''
    '''
    messagers = Dict
    name = Str
    time_gens = Dict
    def __init__(self, *args, **kw):
        '''

        '''
        super(MessagingDisplay, self).__init__(*args, **kw)
        self.color_gen = color8i_generator()

    def register(self, name):
        '''
            @type name: C{str}
            @param name:
        '''
        self.messagers[name] = self.color_gen.next()
        self.time_gens[name] = time_stamp_generator()

    def add_text(self, **kw):
        '''
        '''
        if 'color' in kw:
            c = kw['color']
        else:
            c = None

        if 'name' in kw:
            name = kw['name']
            if c is None:
                c = self.messagers[name]

            ts = self.time_gens[name].next()

            kw['msg'] = ' '.join((ts, kw['msg']))

        else:
            name = 'Null'
            c = 'black'

        kw['color'] = c

        super(MessagingDisplay, self).add_text(**kw)

class MultiPanelMessagingDisplay(HasTraits):
    '''
    '''
    panels = List(StyledTextDisplay)
    messagers = Dict
    width = Float(200)
    height = Float(200)
    title = String('')

    def register(self, name):
        '''
            @type name: C{str}
            @param name:
        '''
        md = MessagingDisplay(name=name)
        md.register(name)
        self.panels.append(md)


    def add_text(self, **kw):
        '''
          
        '''
        for p in self.panels:
            for mk in p.messagers:
                name = kw['name']
                msg = kw['msg']

                color = kw['color'] if 'color' in kw else None

                if mk == name:
                    p.add_text(name=name, msg=msg, color=color)

    def traits_view(self):
        '''
        '''
        v = View(Item('panels', style='custom',
                    show_label=False,
                    editor=ListEditor(use_notebook=True,
                                      page_name='.name',
                                               dock_style='horizontal')),
                title=self.title,
                width=self.width,
                height=self.height,
                resizable=True
                )
        return v
#============= views ===================================

#============= EOF ====================================
