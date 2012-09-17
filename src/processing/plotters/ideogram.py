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
from traits.api import HasTraits, Instance, Any, Int, Str, Float, List
from traitsui.api import View, Item, HGroup, spring, TabularEditor
from chaco.api import ArrayDataSource, ScatterInspectorOverlay
from chaco.tools.api import ScatterInspector
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
from numpy import asarray, linspace, zeros
import math
#============= local library imports  ==========================

from src.graph.stacked_graph import StackedGraph
from src.graph.error_bar_overlay import ErrorBarOverlay
#from src.processing.figure import AgeResult

def weighted_mean(x, errs):
    x = asarray(x)
    errs = asarray(errs)

    weights = asarray(map(lambda e: 1 / e ** 2, errs))

    wtot = weights.sum()
    wmean = (weights * x).sum() / wtot
    werr = wtot ** -0.5
    return wmean, werr

class IdeoResultsTabularAdapter(TabularAdapter):
    columns = [('Age', 'age'),
               ('Error(1s)', 'error')
             ]
    age_format = Str('%0.3f')
    error_format = Str('%0.3f')
class IdeoResult(HasTraits):
    age = Float
    error = Float

class Ideogram(HasTraits):
    ages = None
    errors = None
    graph = Any
    selected_analysis = Any
    analyses = Any

    ideoresults = List
    nsigma = Int(1, enter_set=True, auto_set=False)
    def _nsigma_changed(self):
        self.error_bar_overlay.nsigma = self.nsigma
        self.graph.redraw()

    def build_results(self, display):
        width = lambda x, w = 8:'{{:<{}s}}='.format(w).format(x)
#        floatfmt = lambda x, w = 3:'{{:0.{}f}}'.format(w).format(x)
        floatfmt = lambda x:'{:0.3f}'.format(x)
        attr = lambda n, v:'{}{}'.format(width(n), floatfmt(v))

#        display.add_text(' ')
#        lines = []

#        for ai, ei in zip(self.ages, self.errors):
        for ri in self.ideoresults:
            display.add_text(attr('age', ri.age))
            display.add_text(attr('error', ri.error))


    def build(self, analyses, padding):
        self.ideoresults = []
        self.analyses = analyses
        g = StackedGraph(panel_height=200,
                                equi_stack=False,
                                container_dict=dict(padding=5,
                                                    bgcolor='lightgray')
                                )

        self.graph = g
        g.new_plot(
                   padding=padding)

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')

        g.set_x_title('Age (Ma)')

        g.set_x_title('Age (Ma)')
        g.set_y_title('Relative Probability')

        self.minprob = None
        self.maxprob = None

        gids = list(set([a.gid for a in analyses]))

        pad = 2
        ages = [a.age[0] for a in analyses]
        if not ages:
            return

        xmin = min(ages) - pad
        xmax = max(ages) + pad


        for gid in gids:
            anals = [a for a in analyses if a.gid == gid]
            self._add_ideo(g, anals, xmin, xmax, padding)

        g.set_x_limits(min=xmin, max=xmax)
        return g

    def _add_ideo(self, g, analyses, xmi, xma, padding):
        ages, errors = zip(*[a.age for a in analyses])
        n = 500
        bins = linspace(xmi, xma, n)
        probs = zeros(n)

        ages = asarray(ages)
        wm, we = weighted_mean(ages, errors)
#        self.age = wm
#        self.age_error = we
#        self.ages.append(wm)
#        self.errors.append(we)
        self.ideoresults.append(IdeoResult(age=wm, error=we))
        for ai, ei in zip(ages, errors):
            if abs(ai) < 1e-7:
                continue

            for j, bj in enumerate(bins):
                #calculate the gaussian prob
                #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
                #see http://en.wikipedia.org/wiki/Normal_distribution
                delta = math.pow(ai - bj, 2)
                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))

                #cumulate probablities
                probs[j] += prob

        minp = min(probs)
        maxp = max(probs)
        dp = maxp - minp

        nsigma = 0.954 #2sigma
        s, _p = g.new_series(x=bins, y=probs)
        s, _p = g.new_series([wm], [maxp - nsigma * dp],
                             type='scatter',
#                             marker='plus',
                             marker='circle',
                             marker_size=3,
                             color=s.color)

        self.error_bar_overlay = ebo = ErrorBarOverlay(component=s, nsgima=self.nsigma)
        s.underlays.append(ebo)
        s.xerror = ArrayDataSource([we])

        if self.minprob:
            minp = min(self.minprob, minp)

        if self.maxprob:
            maxp = max(self.maxprob, maxp)

        self.minprob = minp
        self.maxprob = maxp

        g.set_y_limits(min=minp, max=maxp * 1.05)

        self._add_aux_plot(g, ages, errors, padding)

        #set the color
        for a in analyses:
            a.color = s.color


    def _add_aux_plot(self, g, ages, errors, padding):
        g.new_plot(
                   padding=padding, #[padding_left, padding_right, 1, 0],
                   bounds=[50, 100]
                   )
        g.set_grid_traits(visible=False, plotid=1)
        g.set_grid_traits(visible=False, grid='y', plotid=1)

        g.set_axis_traits(tick_visible=False,
                          tick_label_formatter=lambda x:'',
                          axis='y', plotid=1)
        g.set_y_title('Analysis #', plotid=1)
#        g.set_axis_traits(orientation='right', plotid=1, axis='y')

        n = zip(ages, errors)
        n = sorted(n, key=lambda x:x[0])
        ages, errors = zip(*n)

        scatter, _p = g.new_series(ages, range(1, len(ages) + 1, 1),
                                   type='scatter', marker='circle',
                                   marker_size=2,
                                   plotid=1)
        scatter.underlays.append(ErrorBarOverlay(component=scatter))
#        scatter.underlays.append(ErrorBarOverlay(component=s))
        scatter.xerror = ArrayDataSource(errors)

        #add a scatter hover tool
        scatter.tools.append(ScatterInspector(scatter, selection_mode='off'))
        overlay = ScatterInspectorOverlay(scatter,
                    hover_color="red",
                    hover_marker_size=6,
                    )
        scatter.overlays.append(overlay)

        #bind to the metadata
        scatter.index.on_trait_change(self.update_graph_metadata, 'metadata_changed')
        self.metadata = scatter.index.metadata

        g.set_y_limits(min=0, max=len(ages) + 1, plotid=1)


    def update_graph_metadata(self, obj, name, old, new):
##        print obj, name, old, new
        hover = self.metadata.get('hover')
        if hover:
            hoverid = hover[0]
            self.selected_analysis = sorted([a for a in self.analyses], key=lambda x:x.age)[hoverid]

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(HGroup(Item('nsigma'), spring),
                 Item('ideoresults',
                      style='custom',
                      show_label=False,
                      editor=TabularEditor(adapter=IdeoResultsTabularAdapter())


                      )

                 )
        return v

#class MultipleIdeogram(Ideogram):
#    def _build_ideo(self, g):
#        for i in range(3):
#            anals = [a for a in self.analyses if a.gid == i]
#            ages, errors = zip(*[a.age for a in anals])
#            self._add_ideo(g, ages, errors)



#============= EOF =============================================
#g = StackedGraph(panel_height=200,
#                         equi_stack=False
#                         )
#
#        g.new_plot()
#        g.add_minor_xticks()
#        g.add_minor_xticks(placement='opposite')
#        g.add_minor_yticks()
#        g.add_minor_yticks(placement='opposite')
#        g.add_opposite_ticks()
#
#        g.set_x_title('Age (Ma)')
#        g.set_y_title('Relative Probability')
#
##        ages, errors = zip(*[(ai.age, ai.age_err) for ai in self.analyses])
#        ages = self.ages
#        errors = self.errors
#        pad = 1
#        mi = min(ages) - pad
#        ma = max(ages) + pad
#        n = 500
#        bins = linspace(mi, ma, n)
#        probs = zeros(n)
#        g.set_x_limits(min=mi, max=ma)
#
#        ages = asarray(ages)
#        wm, we = weighted_mean(ages, errors)
#        self.age = wm
#        self.age_err = we
##        print ages
##        print errors
##        print 'waieht', wm, we
#        for ai, ei in zip(ages, errors):
#            for j, bj in enumerate(bins):
#                #calculate the gaussian prob
#                #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
#                #see http://en.wikipedia.org/wiki/Normal_distribution
#                delta = math.pow(ai - bj, 2)
#                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))
#
#                #cumulate probablities
#                probs[j] += prob
#
#        minp = min(probs)
#        maxp = max(probs)
#        g.set_y_limits(min=minp, max=maxp * 1.05)
#
#        g.new_series(x=bins, y=probs)
#
#        dp = maxp - minp
#
#        s, _p = g.new_series([wm], [maxp - 0.85 * dp], type='scatter', color='black')
#        s.underlays.append(ErrorBarOverlay(component=s))
#        nsigma = 2
#        s.xerror = ArrayDataSource([nsigma * we])
#
#        g.new_plot(bounds=[50, 100])
