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
from traits.api import HasTraits, Range, Instance
from traitsui.api import View, Item, Group

#============= standard library imports ========================
from numpy import linspace

#============= local library imports  ==========================

from src.graph.graph import Graph
from src.hardware.core.motion.motion_profiler import MotionProfiler



class MotionDesigner(HasTraits):
    canvas = Instance(Graph)
    acceleration = Range(0, 8., 7.62)
    deceleration = Range(0, 8., 7.62)
    velocity = Range(0, 4., 3.81)
    distance = Range(0, 10., 5)
    beam_radius = Range(0, 1.5, 1)
    def _anytrait_changed(self, name, old, new):
        if name in ['acceleration', 'deceleration', 'velocity',
                    'distance', 'beam_radius']:
            self.replot()

    def replot(self):
        g = self.canvas


        g.clear()
        g.new_plot(title = 'Velocity')
        g.new_plot(title = 'Position')

        atime, dtime, vtime = self.velocity_profile(0)

        self.position_profile(1, atime, dtime, vtime)


    def position_profile(self, plotid, atime, dtime, vtime):
        g = self.canvas

        x = [0]
        y = [0]
        #plot accel
        for i in linspace(0, atime, 50):
            x.append(i)

            p = 0.5 * self.acceleration * i ** 2
            y.append(p)

        #plot constant velocity
        yo = p + vtime * self.velocity

        #plot decel
        for i in linspace(0, dtime, 50):
            x.append(atime + vtime + i)
            p = yo + self.velocity * i - 0.5 * self.deceleration * i ** 2
            y.append(p)
        g.new_series(x, y, render_style = 'connectedpoints')


        #plot beam center
        y = [p / 2.0] * 50
        x = linspace(0, atime + vtime + dtime, 50)
        g.new_series(x, y)

        #plot beam radius'
        #include padding in the beam radius
        yl = [pi - self.beam_radius for pi in y]
        yu = [pi + self.beam_radius for pi in y]
        g.new_series(x, yl, color = 'blue')
        g.new_series(x, yu, color = 'blue')


    def velocity_profile(self, plotid):
        g = self.canvas

        v = self.velocity
        #ac = self.acceleration
        #dc = self.deceleration

        d = self.distance
        m = MotionProfiler()



        params = m.calculate_transit_times(d, self)
        atime, dtime, vtime = params
        #error, atime, dtime, cvd = m.check_motion(v, ac, d)
        x = [0]
        y = [0]

#        atime = v / float(ac)
#        dtime = v / float(dc)
        x.append(atime)
        y.append(v)

#        acd = 0.5 * ac * atime ** 2
#        dcd = 0.5 * ac * dtime ** 2
#
#        cvd = d - acd - dcd
#
#        if cvd < 0:
#            #calculate a corrected velocity
#            vc = math.sqrt((2 * d * ac) / 3.)
#            print vc


        x.append(atime + vtime)
        y.append(v)
#
        totaltime = atime + dtime + vtime
        x.append(totaltime)
        y.append(0)
        g.new_series(x, y, plotid = plotid, render_style = 'connectedpoints')
        g.set_y_limits(plotid = plotid, max = self.velocity + 5)


        return atime, dtime, vtime
#============= views ===================================
    def traits_view(self):
        cgrp = Group(
                   Item('acceleration'),
                   Item('deceleration'),
                   Item('velocity'),
                   Item('distance'),
                   Item('beam_radius')
                   )
        v = View(
                 cgrp,
                 Item('canvas', show_label = False,
                    style = 'custom'),
                 resizable = True,
                 width = 800,
                 height = 700
                 )
        return v
    def _canvas_default(self):
        g = Graph()

        return g
if __name__ == '__main__':
    m = MotionDesigner()
    m.replot()
    m.configure_traits()
#============= EOF ====================================
