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
from traits.api import DelegatesTo, \
     Font, HasTraits, Any, Color, Property
from traitsui.api import View, Item, \
    TextEditor, ColorEditor, Handler
#=============standard library imports ========================
from wx import Colour
import sys
#=============local library imports  ==========================


class GraphEditorHandler(Handler):
    def closed(self, info, is_ok):
        '''
        '''
        obj = info.object
        obj.graph_editor = None


class GraphEditor(HasTraits):
    '''
    '''
    graph = Any
    container = Property(depends_on='graph')
    bgcolor = Property(depends_on='bgcolor_')
    bgcolor_ = Color

    title = DelegatesTo('graph', prefix='_title')
    font = Font

    def sync(self):
        '''
        '''
        g = self.graph
        f = 'Helvetica 18'
        if g and g._title_font and g._title_size:
            f = '%s %s' % (g._title_font,
                               g._title_size
                               )
        self.font = f

    def _get_container(self):
        '''
        '''
        return self.graph.plotcontainer

    def _get_bgcolor(self):
        '''
        '''

        bg = self.container.bgcolor
        if isinstance(bg, str):
            bg = Colour().SetFromName(bg)

        return bg

    def _set_bgcolor(self, v):
        '''

        '''

        if sys.platform == 'win32':
            v = [vi / 255. for vi in v]

        self.container.bgcolor = v
#        self.container.invalidate_and_redraw()
        self.container.request_redraw()

    def _font_changed(self):
        '''
        '''
        self._update_()

    def _title_changed(self):
        '''
        '''
        self._update_()

    def _graph_changed(self):
        '''
        '''
        self.sync()

    def _update_(self):
        '''
        '''

        args = str(self.font).split(' ')
        size = args[0]

        font = ' '.join(args[2:])
        self.graph.set_title(self.title, font=font, size=size)

    def traits_view(self):
        '''
        '''
        v = View(Item('bgcolor', editor=ColorEditor()),
               Item('title', editor=TextEditor(enter_set=True,
                                               auto_set=False)),
               Item('font',
                    style='custom',
                    ),
               title='Graph Editor',
               resizable=True,
               handler=GraphEditorHandler,
               x=0.05,
               y=0.1,
               )
        return v
#============= EOF =====================================
