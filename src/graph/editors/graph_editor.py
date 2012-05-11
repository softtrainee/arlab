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



from src.graph.stacked_graph import StackedGraph
'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import DelegatesTo, \
     Font, HasTraits, Any, Color, Property, Int, Str
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
    global_tick_font = Font
    global_axis_title_font = Font

    xspacing = Int
    yspacing = Int
    padding = Str
    def sync(self):
        '''
        '''
        g = self.graph
        f = 'Helvetica 12'
        if g and g._title_font and g._title_size:
            f = '%s %s' % (g._title_font,
                               g._title_size
                               )
        self.font = f

        if g and g.plots[0]:
            f = g.plots[0].x_axis.tick_label_font
            n = f.face_name
            if not n:
                n = 'Helvetica'
            self.global_tick_font = '{} {}'.format(n, f.size)

        if g and g.plots[0]:
            f = g.plots[0].x_axis.title_font
            n = f.face_name
            if not n:
                n = 'Helvetica'
            self.global_axis_title_font = '{} {}'.format(n, f.size)

        p = self.graph.plots[0].padding
        if isinstance(p, list):
            self.padding = ','.join(map(str, p))
        else:
            self.padding = p

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
        font, size = self._get_font_args(self.font)
        self.graph.set_title(self.title, font=font, size=size)

    def _get_font_args(self, f):

        args = str(f).split(' ')
        size = args[0]

        font = ' '.join(args[2:])
        return font, size

    def _global_tick_font_changed(self):
        self._change_global_font(self.global_tick_font, 'tick_label_font')

    def _global_axis_title_font_changed(self):
        self._change_global_font(self.global_axis_title_font, 'title_font')

    def _change_global_font(self, f, key):
        g = self.graph
        font = str(f)
        for po in g.plots:
            setattr(po.x_axis, key, font)
            setattr(po.y_axis, key, font)

        self.graph.redraw()

    def _xspacing_changed(self):
        try:
            self.graph.plotcontainer.spacing = (self.xspacing,
                                                self.yspacing)
        except:
            self.graph.plotcontainer.spacing = self.xspacing
        self.graph.redraw()

    def _yspacing_changed(self):
        try:
            self.graph.plotcontainer.spacing = (self.xspacing,
                                                self.yspacing)
        except:
            self.graph.plotcontainer.spacing = self.yspacing

        self.graph.redraw()

    def _padding_changed(self):
        try:
            p = map(int, self.padding.split(','))
            if len(p) == 1:
                p = p[0]

            if isinstance(self.graph, StackedGraph):
                pa = self.graph.plots[0].padding
                #dont change the top padding of the first plot
                p[2] = pa[2]
                self.graph.plots[0].padding = [p[0], p[1], pa[2], p[3]]
                for ps in self.graph.plots[1:-1]:
                    ps.padding = [p[0], p[1], 0, 0]
                self.graph.plots[-1].padding = [p[0], p[1], p[2], 0]
            else:
                for pi in self.graph.plots:
                    pi.padding = p

            self.graph.redraw()

        except Exception, e:
#            print e
            pass

    def traits_view(self):
        '''
        '''
        v = View(Item('bgcolor', editor=ColorEditor()),
               Item('title', editor=TextEditor(enter_set=True,
                                               auto_set=False)),
               Item('font',
                    style='custom',
                    ),

               Item('global_tick_font', style='custom'),
               Item('global_axis_title_font', style='custom'),
               Item('xspacing'),
               Item('yspacing'),
               Item('padding'),
               title='Graph Editor',
               resizable=True,
               handler=GraphEditorHandler,
               x=0.05,
               y=0.1,
               )
        return v
#============= EOF =====================================
