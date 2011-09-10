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
#============= enthought library imports =======================
from traits.api import HasTraits, Bool, Range, Any, DelegatesTo, on_trait_change, \
    Float, Button, Instance, Enum
from traitsui.api import View, Item, Group, ButtonEditor
import apptools.sweet_pickle as pickle
from traitsui.menu import Action
from pyface.api import FileDialog, OK
#============= standard library imports ========================
import math
import os
#============= local library imports  ==========================
from src.graph.graph import Graph
from jog_pattern import JogPattern
from src.managers.manager import Manager, ManagerHandler
from src.helpers.paths import jog_dir


class JogHandler(ManagerHandler):
    def dump(self, info):
        obj = info.object

        dlg = FileDialog(action='save as', default_directory=jog_dir)
        if dlg.open() == OK:
            with open(dlg.path, 'w') as f:
#                pickle.dump(obj.opattern, f)
                pickle.dump((obj.ipattern, obj.opattern), f)

    def load_file(self, info):
        obj = info.object
        obj.load_file()

#                obj.opattern = pickle.load(f)


class JogManager(Manager):
    canvas = Instance(Graph)
    beam_diam = Range(0.0001, 2, 0.5)
    parent = Any
    jog = DelegatesTo('parent')
    jog_label = DelegatesTo('parent')
    _jogging = DelegatesTo('parent')

    bind = Bool(True)
    ipattern = Instance(JogPattern)
    opattern = Instance(JogPattern)

    kind = Enum('line_spiral', 'square_spiral')

    cx = Float
    cy = Float

    handler_klass = JogHandler
    def load_file(self, name=None):
        if name is None:
            dlg = FileDialog(action='open', default_directory=jog_dir)
            if dlg.open() == OK:
                path = dlg.path
            else:
                return
        else:
            path = os.path.join(jog_dir, name)

        with open(path, 'r') as f:
            self.ipattern, self.opattern = pickle.load(f)
            self.ipattern.parent = self
            self.opattern.parent = self
            self.replot()

    def get_jogs(self):
        '''
            return a list of valid file names
        '''
        return [os.path.splitext(path)[0]
                for path in os.listdir(jog_dir)
                    if os.path.isfile(os.path.join(jog_dir, path))]

#    def load_file(self, name = None):
#        if name is None:
#            name = self.name
#
#        with open(os.path.join(jog_dir, name), 'r') as f:
#            try:
#                self.ipattern, self.opattern = pickle.load(f)
#            except:
#                pass

#    def dump(self, name = None):
#        print 'adfaf', name
#        if name is None:
#            name = self.name
#
#
#        with open(os.path.join(jog_dir, name), 'w') as f:
#            pickle.dump((self.ipattern, self.opattern), f)

#    @on_trait_change('parent.x,parent.y')
    def pchange(self, obj, name, old, new):
        if not self._jogging:
            self.trait_set(**{'c%s' % name: new})
            self.replot()

    @on_trait_change('ipattern.+')
    def change(self, o, n, oo, nn):
        if self.bind:
            if n not in ['show_overlap', 'show_path', 'transit_time']:
                self.opattern.trait_set(**{n:nn})
                self.replot()

    @on_trait_change('opattern.+')
    def ochange(self, o, n, oo, nn):
        if self.bind:
            if n not in ['show_overlap', 'show_path', 'transit_time']:
                self.ipattern.trait_set(**{n:nn})
                self.replot()

    def _anytrait_changed(self, name, old, new):
        if name in ['beam_diam', 'kind', 'cx', 'cy']:

            setattr(self.opattern, name, new)
            setattr(self.ipattern, name, new)
            self.replot()

    def replot(self):
        self.canvas.clear()
        self.canvas.new_plot(padding=10)
        cx = self.cx
        cy = self.cy

        #draw sample hole
        self.circle(cx, cy, 1, edge_width=3)

        sx, sy = self.opattern.do_spiral(self.kind)
        self.ipattern.do_spiral(self.kind, sx=sx, sy=sy)

    def circle(self, cx, cy, r, face_color=(1, 1, 1, 0), line_color='black', alpha=1, edge_width=2):
        if cx is None or cy is None:
            return

        g = self.canvas

        x = []
        y = []
        for i in range(361):
            t = math.radians(i)
            x.append(cx + r * math.cos(t))
            y.append(cy + r * math.sin(t))
        g.new_series(x, y,
                     type='polygon',
                     face_color=face_color,
                     alpha=alpha,
                     edge_width=edge_width
                     )

    def update_position(self, x, y):
        self.replot()
        self.circle(x, y, 0.1, face_color=(1, 1, 0))
#============= views ===================================
    def traits_view(self):

        control_grp = Group(
                            Group(
                              Item('jog', editor=ButtonEditor(label_value='jog_label'), show_label=False),
                              Item('bind'),
                              Item('beam_diam', label='Beam Diam.'),
                              Item('kind', show_label=False),
                              label='Main'
                              ),
                            Group(
                                  Item('ipattern', show_label=False, style='custom'),
                                  label='In'

                                  ),
                            Group(
                                  Item('opattern', show_label=False, style='custom'),
                                  label='Out'
                                  ),

                            layout='tabbed'
                            )

        save = Action(name='save',
                    action='dump')
        load = Action(name='load',
                    action='load_file')

        v = View(
                 control_grp,
                 Item('canvas', style='custom', show_label=False),
                 resizable=True,
                 title='Jog Manager',
                 handler=self.handler_klass,
                 buttons=[save, load]
               )
        return v
    def _canvas_default(self):

        g = Graph(
                  width=300,
                  height=300,
                  container_dict=dict(
                                        padding=20
                                        )
                  )

        return g
    def _opattern_default(self):
        s = JogPattern(direction='out',
                 parent=self,
                 cx=0,
                 cy=0,
                 beam_diam=self.beam_diam
                 )
        return s
    def _ipattern_default(self):
        s = JogPattern(direction='in',
                 parent=self,
                 cx=0,
                 cy=0,
                 beam_diam=self.beam_diam
                 )
        return s
class DummyParent(HasTraits):
    jog = Button
    _jogging = Bool(False)

if __name__ == '__main__':
#    main()
    j = JogManager(parent=DummyParent())
    j.replot()
    j.configure_traits()
#============= EOF ====================================
