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
#from traits.api import HasTraits
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from experiment import ExperimentNode
from src.graph.stacked_graph import StackedGraph
class SpectrumNode(ExperimentNode):
    def replot(self):
        g = StackedGraph(panel_height=200,
                         equi_stack=False
                         )

        g.new_plot()

        ar39s = [0, 0.1, 0.5, 1]
        ages = [10, 10.4, 20, 30]
        errors = [1, 1, 3, 2]

        xs = []
        ys = []
        es = []
        sar = sum(ar39s)
        prev = 0

        for ai, ei, ar in zip(ages, errors, ar39s):
#            print ai, ei
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
        g.set_y_limits(min=min(ys) * 0.95, max=max(ys) * 1.05)
#============= EOF =============================================
