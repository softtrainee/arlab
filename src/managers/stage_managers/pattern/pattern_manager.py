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
from traits.api import Enum, Instance, Button, Str, Property, Event, Bool
from traitsui.api import View, Item, HGroup, InstanceEditor
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
from threading import Thread

#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.paths import pattern_dir
from src.helpers.filetools import unique_path
from src.helpers.logger_setup import setup
from src.graph.graph import Graph
from src.managers.stage_managers.pattern.patterns import Pattern, \
     LineSpiralPattern, SquareSpiralPattern, \
     RandomPattern, PolygonPattern, ArcPattern
import time
from pyface.timer.do_later import do_later
class PatternManager(Manager):
    kind = Property(Enum('Arc',
                         'Polygon',

                         'LineSpiral',
                'SquareSpiral',

                'Random'
                ), depends_on='_kind')
    _kind = Enum(
                 'Arc',
                 'Polygon',
                 'LineSpiral',
                'SquareSpiral',
                'Random'
                )

    pattern = Instance(Pattern, ())
    load_button = Button('Load')
    save_button = Button('Save')

    execute_button = Event
    execute_label = Property(depends_on='_alive')
    _alive = Bool(False)

    design_button = Button('Design')
    pattern_name = Str

    def _get_execute_label(self):
        return 'Execute' if not self._alive else 'Stop'

    def _execute_button_fired(self):
        if self._alive:
            print 'ex'
        else:
            print 'stop'

        self._alive = not self._alive
#            self.execute_pattern()
    def _design_button_fired(self):
        self.edit_traits(view='pattern_maker_view')

    def get_pattern_names(self):
        return self.get_file_list(pattern_dir, extension='.lp')

    def stop_pattern(self):
        self.info('User requested stop')
        self._alive = False
        self.parent.stage_controller.stop()

    def execute_pattern(self, pattern_name=None, use_current=False):
        if pattern_name is not None:
            #open pattern from file
            self.load_pattern(path=os.path.join(pattern_dir,
                                                            '{}.lp'.format(pattern_name)
                                                            ))
        elif not use_current:
            #===================================================================
            #for testing
            # path = os.path.join(pattern_dir, 'testpattern.lp')
            # self.load_pattern(path = path)
            #===================================================================
            #open a file dialog to choose pattern
            self.load_pattern()

        if self.pattern is not None:
            self._alive = True
#            self.edit_traits()
            do_later(self.edit_traits)
            t = Thread(target=self._execute_)
            t.start()
        else:
            err = 'invalid pattern name {}'.format(pattern_name)
            self.info(err)
            return err

    def _execute_(self):
        self.info('started pattern {}'.format(self.pattern_name))
        pat = self.pattern
        controller = self.parent.stage_controller

        pat.cx = controller._x_position
        pat.cy = controller._y_position

        pts = pat.points_factory()
        if self.kind == 'ArcPattern':
            controller.single_axis_move('x', pat. radius)
            controller.arc_move(pat.cx, pat.cy, pat.degrees)
        else:
            controller.multiple_point_move(pts)

        if controller.simulation:
            time.sleep(1)

        if self._alive:
            self.info('finished pattern {}'.format(self.pattern_name))
            self.close_ui()

    def load_pattern(self, path=None):
        self.pattern = None
        if path is None:
            path = self.open_file_dialog(default_directory=pattern_dir)

        if path is not None and os.path.isfile(path):
            with open(path, 'rb') as f:
                self.pattern = pickle.load(f)

                self._kind = self.pattern.__class__.__name__.partition('Pattern')[0]
                self.pattern_name = os.path.basename(path).split('.')[0]
                self.info('loaded {} from {}'.format(self.pattern_name, path))
                self.pattern.replot()

    def save_pattern(self):
        if not self.pattern_name:
            path, _cnt = unique_path(pattern_dir, 'pattern', filetype='lp')
            self.pattern_name = os.path.basename(path).split('.')[0]
        else:
            path = os.path.join(pattern_dir, '{}.lp'.format(self.pattern_name))

        with open(path, 'wb') as f:
            pickle.dump(self.pattern, f)
        self.info('saved {} pattern to {}'.format(self.pattern_name, path))

    def pattern_factory(self, kind):
        pattern = globals()['{}Pattern'.format(kind)]()

        pattern.replot()
        return pattern

    def view_a(self):
        v = View(self._button_factory('execute_button', 'execute_label'),
                 Item('design_button', show_label=False)
                 )
        return v

    def traits_view(self):
        v = View(Item('pattern', show_label=False,
                       style='custom',
                       editor=InstanceEditor(view='graph_view')),
                 handler=self.handler_klass,
                 title=self.pattern_name
                 )
        return v

    def pattern_maker_view(self):
        v = View(HGroup(Item('pattern_name', label='Name'), Item('kind')),
                 HGroup(Item('save_button', show_label=False),
                        Item('load_button', show_label=False)),
                 Item('pattern', style='custom', show_label=False),
                 resizable=True,
                 width=520,
                 height=750,
                 title='Pattern Maker'
                 )
        return v

    def _graph_default(self):

        g = Graph(
                  width=400,
                  height=400,
                  container_dict=dict(
                                        padding=30
                                        )
                  )
        return g

    def _pattern_default(self):
        return self.pattern_factory(self.kind)

    def _save_button_fired(self):
        self.save_pattern()

    def _load_button_fired(self):
        self.load_pattern()

    def _get_kind(self):
        return self._kind

    def _set_kind(self, v):
        self._kind = v

        #sync params
#        prev_pat = self.pattern
        self.pattern = self.pattern_factory(v)
#        for a in self.pattern.traits():
#            try:
#                print a
#                setattr(self.pattern, a, getattr(prev_pat, a))
#            except AttributeError, e:
#                print e

if __name__ == '__main__':
    setup('pattern')
    pm = PatternManager()
    pm.configure_traits(view='pattern_maker_view')
#============= EOF ====================================
