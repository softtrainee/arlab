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
from traits.api import Enum, Instance, Button, Str, Property, Event, Bool, DelegatesTo
from traitsui.api import View, Item, HGroup, InstanceEditor, spring
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
from src.canvas.canvas2D.image_underlay import ImageUnderlay
from src.image.image import Image
from src.image.image_helper import clone, copy
class PatternManager(Manager):
    kind = Property(Enum(
                         'Polygon',
                         'Arc',

                         'LineSpiral',
                'SquareSpiral',

                'Random'
                ), depends_on='_kind')
    _kind = Enum(
                 'Polygon',
                 'Arc',
                 'LineSpiral',
                'SquareSpiral',
                'Random'
                )

    pattern = Instance(Pattern)
    load_button = Button('Load')
    save_button = Button('Save')

    execute_button = Event
    execute_label = Property(depends_on='_alive')
    _alive = Bool(False)

    design_button = Button('Design')
    pattern_name = Property(depends_on='pattern')

    show_patterning = Bool(True)
    record_patterning = Bool(False)

    window_x = 0.75
    window_y = 0.05
    def _get_pattern_name(self):
        if not self.pattern:
            return 'Pattern'
        else:
            return self.pattern.name

    def _get_execute_label(self):
        return 'Execute' if not self._alive else 'Stop'

    def _execute_button_fired(self):
        if self._alive:
            self.stop_pattern()
        else:
            self.execute_pattern()

    def _design_button_fired(self):
        self.edit_traits(view='pattern_maker_view', kind='livemodal')

    def get_pattern_names(self):
        return self.get_file_list(pattern_dir, extension='.lp')

    def stop_pattern(self):
        self.info('User requested stop')
        self._alive = False
        self.parent.stage_controller.stop()

        if self.record_patterning:
            self.parent.stop_recording()

    def execute_pattern(self, pattern_name=None):
        if pattern_name is not None:
            #open pattern from file
            self.load_pattern(path=os.path.join(pattern_dir,
                                                            '{}.lp'.format(pattern_name)
                                                            ))
            #===================================================================
            #for testing
            # path = os.path.join(pattern_dir, 'testpattern.lp')
            # self.load_pattern(path = path)
            #===================================================================
        elif self.pattern is None:
            #open a file dialog to choose pattern
            self.load_pattern()
#            
        if self.pattern is not None:
            use_image_underlay = True
            if use_image_underlay:
                img = self.parent.video.get_frame()

#                p = '/Users/ross/Desktop/foo2.tiff'
#                img = Image()
#                img.load(p)

#                px = float(self.parent._camera_xcoefficients[1])
                px = float(self.parent._camera_xcoefficients.split(',')[1])
                print px
                self.pattern.set_mapping(px)
                self.pattern.reset_graph(with_image=True)
#                self.pattern.set_image(img.source_frame)
#                self.pattern.set_image(img.as_numpy_array())
                self.pattern.set_image(img)

            self._alive = True
            if self.show_patterning:
                do_later(self.edit_traits)

            t = Thread(target=self._execute_)
            t.start()
        else:
            err = 'invalid pattern name {}'.format(pattern_name)
            self.info(err)
            return err

    def _execute_(self):
#        import threading
#        print threading.currentThread()
        self.info('started pattern {}'.format(self.pattern_name))

        if self.record_patterning:
            self.parent.start_recording(basename=self.pattern_name)


        pat = self.pattern
        controller = self.parent.stage_controller

        pat.cx = controller._x_position
        pat.cy = controller._y_position

        pts = pat.points_factory()
        if self.kind == 'ArcPattern':
            controller.single_axis_move('x', pat.radius)
            controller.arc_move(pat.cx, pat.cy, pat.degrees)
        else:
            multipoint = False
            if multipoint:
                controller.multiple_point_move(pts)
            else:

#                self.parent.video.new_graphics_container()
#                px = None
#                py = None
                for x, y in pts:
                    xi, yi = pat.map_pt(x, y)
                    pat.graph.set_data([xi], series=1, axis=0)
                    pat.graph.set_data([yi], series=1, axis=1)

#                    if px is not None:
#                        self.parent.video.graphics_container.add_line([(px, py), (xi, yi)])
#
#                    px = xi
#                    py = yi

                    pat.graph.redraw()

                    controller.linear_move(x, y, block=True)
                    if controller.simulation:
                        time.sleep(0.25)

        pat.graph.set_data([], series=1, axis=0)
        pat.graph.set_data([], series=1, axis=1)

        if controller.simulation:
            time.sleep(1)

        if self._alive:
            self.info('finished pattern {}'.format(self.pattern_name))
            if self.record_patterning:
                self.parent.stop_recording()
#            self.parent.video.graphics_container = None

            self.close_ui()
        self._alive = False

    def load_pattern(self, path=None):
        if path is None:
            path = self.open_file_dialog(default_directory=pattern_dir)

        if path is not None and os.path.isfile(path):
            self.pattern = None
            with open(path, 'rb') as f:
                p = pickle.load(f)
                p.path = path
                self.pattern = p
                self._kind = self.pattern.__class__.__name__.partition('Pattern')[0]
                self.info('loaded {} from {}'.format(self.pattern_name, path))
                self.pattern.replot()

    def save_pattern(self):
        if not self.pattern_name:
            path, _cnt = unique_path(pattern_dir, 'pattern', filetype='lp')
        else:
            path = os.path.join(pattern_dir, '{}.lp'.format(self.pattern_name))

        self.pattern.path = path
        with open(path, 'wb') as f:
            pickle.dump(self.pattern, f)
        self.info('saved {} pattern to {}'.format(self.pattern_name, path))

    def pattern_factory(self, kind):
        pattern = globals()['{}Pattern'.format(kind)]()

        pattern.replot()
        return pattern

    def execute_view(self):
        v = View(
                 HGroup(Item('pattern_name', label='Name', style='readonly')),

                 self._button_factory('execute_button', 'execute_label', enabled='object.pattern is not None'),
                 Item('design_button', show_label=False),
                 Item('load_button', show_label=False),
                 )
        return v

    def traits_view(self):
        print 'name', self.pattern_name, len(self.pattern_name)
        v = View(Item('pattern', show_label=False,
                       style='custom',
                       editor=InstanceEditor(view='graph_view')),
                 handler=self.handler_klass,
                 title=self.pattern_name,

                 x=self.window_x,
                 y=self.window_y
                 )
        return v

    def pattern_maker_view(self):
        v = View(
                 HGroup(Item('pattern_name', label='Name'), Item('kind')),
                 HGroup(Item('save_button', show_label=False),
                        Item('load_button', show_label=False)),
                 Item('pattern', style='custom', editor=InstanceEditor(view='maker_view'),
                       show_label=False),
                  resizable=True,
                 width=425,
                 height=580,
                 title='Pattern Maker',
                 buttons=['OK', 'Cancel']
#                 kind='livemodal'
                 )
        return v

#    def _graph_default(self):
#
#        g = Graph(
#                  width=100,
#                  height=100,
#                  container_dict=dict(
#                                        padding=30
#                                        )
#                  )
#        return g

    def _pattern_default(self):
        return self.pattern_factory(self.kind)

    def _save_button_fired(self):
        self.save_pattern()

    def _load_button_fired(self):
        self.load_pattern()

        info = self.pattern.edit_traits(kind='modal')

        if not info.result:
            self.pattern = None



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
#    pm.configure_traits(view='execute_view')
#============= EOF ====================================
