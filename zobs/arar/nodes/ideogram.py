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
# from traits.api import HasTraits
# from traitsui.api import View, Item, TableEditor
from chaco.api import ArrayDataSource, ScatterInspectorOverlay
from chaco.tools.api import ScatterInspector
#============= standard library imports ========================
from numpy import asarray, linspace, zeros
import math
#============= local library imports  ==========================
from experiment import ExperimentNode
from src.graph.stacked_graph import StackedGraph
from src.graph.error_bar_overlay import ErrorBarOverlay

def weighted_mean(x, errs):
    x = asarray(x)
    errs = asarray(errs)

    weights = asarray(map(lambda e: 1 / e ** 2, errs))

    wtot = weights.sum()
    wmean = (weights * x).sum() / wtot
    werr = wtot ** -0.5
    return wmean, werr

class IdeogramNode(ExperimentNode):

    def replot(self):
        if not self.analyses:
            return

        g = StackedGraph(panel_height=200,
                         equi_stack=False
                         )

        g.new_plot()
        g.add_minor_xticks()
        g.add_minor_xticks(placement='opposite')
        g.add_minor_yticks()
        g.add_minor_yticks(placement='opposite')
        g.add_opposite_ticks()

        g.set_x_title('Age (Ma)')
        g.set_y_title('Relative Probability')

        ages, errors = zip(*[(ai.age, ai.age_err) for ai in self.analyses])

        pad = 1
        mi = min(ages) - pad
        ma = max(ages) + pad
        n = 500
        bins = linspace(mi, ma, n)
        probs = zeros(n)
        g.set_x_limits(min=mi, max=ma)

        ages = asarray(ages)
        wm, we = weighted_mean(ages, errors)
        self.age = wm
        self.age_err = we
#        print ages
#        print errors
#        print 'waieht', wm, we
        for ai, ei in zip(ages, errors):
            for j, bj in enumerate(bins):
                # calculate the gaussian prob
                # p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
                # see http://en.wikipedia.org/wiki/Normal_distribution
                delta = math.pow(ai - bj, 2)
                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))

                # cumulate probablities
                probs[j] += prob

        minp = min(probs)
        maxp = max(probs)
        g.set_y_limits(min=minp, max=maxp * 1.05)

        g.new_series(x=bins, y=probs)

        dp = maxp - minp

        s, _p = g.new_series([wm], [maxp - 0.85 * dp], type='scatter', color='black')
        s.underlays.append(ErrorBarOverlay(component=s))
        nsigma = 2
        s.xerror = ArrayDataSource([nsigma * we])

        g.new_plot(bounds=[50, 100])
        g.add_minor_xticks(plotid=1, placement='opposite')

        g.add_minor_yticks(plotid=1)
        g.add_minor_yticks(plotid=1, placement='opposite')

        g.add_opposite_ticks(plotid=1)

        g.set_y_title('Analysis #', plotid=1)
        g.set_axis_traits(orientation='right', plotid=1, axis='y')

        n = zip(ages, errors)
#        ages.sort()
        n = sorted(n, key=lambda x:x[0])
        ages, errors = zip(*n)
#        print ages, errors
#        for ni in n:
#            print ni
        scatter, _p = g.new_series(ages, range(1, len(ages) + 1, 1), type='scatter', marker='circle', plotid=1)
        scatter.underlays.append(ErrorBarOverlay(component=s))
        scatter.xerror = ArrayDataSource(errors)

        # add a scatter hover tool
        scatter.tools.append(ScatterInspector(scatter, selection_mode='off'))
        overlay = ScatterInspectorOverlay(scatter,
                    hover_color="red",
                    hover_marker_size=6,
                    )
        scatter.overlays.append(overlay)

        # bind to the metadata
        scatter.index.on_trait_change(self.update_graph_metadata, 'metadata_changed')
        self.metadata = scatter.index.metadata

        g.set_y_limits(min=0, max=len(ages) + 1, plotid=1)
        return g

    def update_graph_metadata(self, obj, name, old, new):
#        print obj, name, old, new
        hover = self.metadata.get('hover')
        if hover:
            hoverid = hover[0]
            self.selected_analysis = sorted([a for a in self.analyses], key=lambda x:x.age)[hoverid]


#============= EOF =============================================
