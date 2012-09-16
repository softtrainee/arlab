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

from src.graph.stacked_graph import StackedGraph
#============= standard library imports ========================
from numpy import array
#============= local library imports  ==========================

class Spectrum(object):

    def build(self, analyses, padding):
        if not analyses:
            return

        g = StackedGraph(panel_height=200, equi_stack=False,
                         container_dict=dict(padding=5,
                                             bgcolor='lightgray')
                         )
        g.new_plot(padding=padding)
        g.set_x_title('cumulative 39Ar')

        g.set_y_title('Age (Ma)')

        gids = list(set([a.gid for a in analyses]))
        for gid in gids:
            anals = [a for a in analyses if a.gid == gid]
            self._add_spectrum(g, anals)
        return g

    def _add_spectrum(self, g, analyses):

        ages, errors = zip(*[a.age for a in analyses])
        ar39s = [a.signals['Ar39'].value for a in analyses]

        xs = []
        ys = []
        es = []
        sar = sum(ar39s)
        prev = 0

        for ai, ei, ar in zip(ages, errors, ar39s):
            xs.append(prev)
            ys.append(ai)
            es.append(ei)

            s = 100 * ar / sar

            xs.append(s)
            ys.append(ai)
            es.append(ei)
            prev = s

        ys.append(ai)
        es.append(ei)
        xs.append(100)

        #main age line
#        g.new_series(xs, ys)
        #error box
        ox = xs[:]
        xs.reverse()
        xp = ox + xs

        yu = [yi + ei for (yi, ei) in zip(ys, es)]

        yl = [yi - ei for (yi, ei) in zip(ys, es)]
        yl.reverse()

        yp = yu + yl
        g.new_series(x=xp, y=yp, type='polygon')
        pad = 0.1
        g.set_y_limits(min=min(ys) * (1 - pad), max=max(ys) * (1 + pad))

        ages = array(ages)
        self.age = ages.mean()
        self.age_error = ages.std()


        return g

#============= EOF =============================================
