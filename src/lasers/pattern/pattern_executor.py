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
from traits.api import  Any, Bool
#============= standard library imports ========================
import os
import cStringIO
#============= local library imports  ==========================
from src.paths import paths
from src.lasers.pattern.patternable import Patternable
import time
from threading import Thread


class PatternExecutor(Patternable):
    controller = Any
    show_patterning = Bool(False)
    _alive = Bool(False)
    
    def start(self, show=False):
        self._alive = True
        
        if show:
            self.show_pattern()

        if self.pattern:
            self.pattern.clear_graph()

    def finish(self):
        self._alive = False
        self.close_pattern()

    def set_current_position(self, x, y, z):
        if self.isPatterning():
            graph = self.pattern.graph
            graph.set_data([x], series=1, axis=0)
            graph.set_data([y], series=1, axis=1)

            graph.add_datum((x, y), series=2)

            graph.redraw()
    
            
    def load_pattern(self, name_or_pickle):
        '''
            look for name_or_pickle in local pattern dir
            
            if not found try interpreting name_or_pickle is a pickled name_or_pickle
            
        '''
        path = None
        if name_or_pickle is None:
            path = self.open_file_dialog()
            if path is None:
                return
        else:
            path = self.is_local_pattern(name_or_pickle)

        if path:
            fp = open(path, 'rb')
        else:
            #convert name_or_pickle into a file like obj
            fp = cStringIO.StringIO()
            fp.write(name_or_pickle)

        pattern = self._load_pattern(fp, path)
        self.on_trait_change(self.stop, 'canceled')
        return pattern

    def is_local_pattern(self, name):
        pname = name
        if not name.endswith('.lp'):
            pname = name + '.lp'

        path = os.path.join(paths.pattern_dir, pname)
        if os.path.isfile(path):
            return path

    def stop(self):
        self.info('User requested stop')
        self._alive = False
        if self.controller:
            self.controller.stop()

        if self.pattern:
            self.controller.linear_move(self.pattern.cx, self.pattern.cy)
            self.pattern.close_ui()
            self.info('Pattern {} stopped'.format(self.pattern_name))

    def isPatterning(self):
        return self._alive

    def close_pattern(self):
        if self.pattern:
            self.pattern.close_ui()

    def show_pattern(self):
        self.pattern.window_x=50
        self.pattern.window_y=50
        self.open_view(self.pattern, view='graph_view')

    def execute(self, block=False):
        '''
            if block is true wait for patterning to finish
            before returning
        '''
        self.start(show=self.show_patterning)

        t = Thread(target=self._execute)
        t.start()

        if block:
            t.join()

            self.finish()

    def _execute(self):
        pat = self.pattern
        if pat:
            self.info('starting pattern {}'.format(pat.name))
            pat.cx, pat.cy = self.controller._x_position, self.controller._y_position
            for ni in range(pat.niterations):
                if not self.isPatterning():
                    break

                self.info('doing pattern iteration {}'.format(ni))
                self._execute_iteration()
#                time.sleep(0.1)

            self.controller.linear_move(pat.cx, pat.cy)
            self.pattern.close_ui()
            self.info('finished pattern')

    def _execute_iteration(self):
        controller = self.controller
        pattern = self.pattern
        if controller is not None:
            
            kind = pattern.kind
            if kind == 'ArcPattern':
                self._execute_arc(controller, pattern)
            elif kind == 'CircularContourPattern':

                self._execute_contour(controller, pattern)
            else:
                self._execute_points(controller, pattern)
#                multipoint = False
#                if multipoint:
#                    controller.multiple_point_move(pts)
#                else:
#                    if controller.simulation:
#                        self._simulate_pattern(pattern)
#                    else:
#    #                    graph = pattern.graph
#                        for x, y in pts:
#    #                        graph.set_data([x], series=1, axis=0)
#    #                        graph.set_data([y], series=1, axis=1)
#    #                        graph.redraw()
#                            controller.linear_move(x, y, block=True,
#                                                   velocity=pattern.velocity)
    def _execute_points(self, controller, pattern, multipoint=False):
        pts = pattern.points_factory()
        if multipoint:
            controller.multiple_point_move(pts)
        else:
            for x, y in pts:
                if not self.isPatterning():
                    break

                controller.linear_move(x, y, block=True,
                                       velocity=pattern.velocity)

    def _execute_contour(self, controller, pattern):
        for ni in range(pattern.nsteps):
            if not self.isPatterning():
                break

            r = pattern.radius * (1 + ni * pattern.percent_change)
            self.info('doing circular contour {} {}'.format(ni + 1, r))
            controller.single_axis_move('x', pattern.cx + r,
                                        block=True)
            controller.arc_move(pattern.cx, pattern.cy, 360,
                                block=True)
            time.sleep(0.1)

    def _execute_arc(self, controller, pattern):
        controller.single_axis_move('x', pattern.radius, block=True)
        controller.arc_move(pattern.cx, pattern.cy, pattern.degrees, block=True)

#============= EOF =============================================
