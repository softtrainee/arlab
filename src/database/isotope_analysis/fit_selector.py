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
from traits.api import HasTraits, List, Any, on_trait_change
from traitsui.api import View, Item, ListEditor, InstanceEditor, Group
#============= standard library imports ========================
import re
#============= local library imports  ==========================
from analysis_parameters import AnalysisParameters


class FitSelector(HasTraits):
    analysis = Any
    graph = Any
    fits = List(AnalysisParameters)
    _suppress_update = False
    _plot_cache = None
    def _analysis_changed(self):
        if self.analysis:
            if self.analysis.isotope_keys:
                keys = list(self.analysis.isotope_keys)
                key = lambda x: re.sub('\D', '', x)
                keys = sorted(keys, key=key, reverse=True)

                n = len(keys) - 1
                self.fits = list(map(lambda x:self._param_factory(n, x), enumerate(keys)))
                self._schanged(None, None, None)

    def _param_factory(self, n, arg):

        i, name = arg
        try:
            reg = self.graph.regressors[n - i]
            fit = reg.fit
            fo = self.graph.get_filter_outliers(n - i)
#            print reg.filter_outliers
            inte = reg.predict(0)
            er = reg.coefficient_errors[-1]
            if fit == 'average':
                fit = u'average \u00b1' + reg.error_calc.upper()
        except IndexError:
            inte, er, fit = 0, 0, '---'

        obj = AnalysisParameters(name=name,
                                 fit=fit,
                                 filter_outliers=fo,
                                 _intercept=inte,
                                 _error=er,
                                 )
        return obj


    @on_trait_change('fits:show')
    def _schanged(self, obj, name, new):
#        print obj, name, new
#        n = len(self.fits) - 1
#        plotid = n - self.fits.index(obj)
#        g = self.graph
#        ss = [a.show for a in self.fits]
#        print self.graph
#        for i, a in enumerate(self.fits):
#            print a.name, a.show
#            if a.show:
        if self._plot_cache is None:
            comps = self.graph.plotcontainer.components
            self._plot_cache = comps
#        comps = list(set(self._plot_cache + self.graph.plotcontainer.components))
#        comps = self.graph.plotcontainer.components
        plots = [p for p, a in zip(self._plot_cache, reversed(self.fits)) if a.show]

        for p, a in zip(self._plot_cache, reversed(self.fits)):
            if not a.show:
                p.visible = False
            else:
                p.visible = True
#        self._plot_cache = [p for p, a in zip(comps, self.fits) if not a.show]

        self.graph.plotcontainer._components = plots
        self.graph.set_paddings()
        self.graph._update_bounds(self.graph.plotcontainer.bounds, plots)

        for i, p in enumerate(reversed(plots)):
            params = dict(orientation='right' if i % 2 else 'left',
                          axis_line_visible=False
                          )
            pi = self._plot_cache.index(p)
            self.graph.set_axis_traits(pi, 'y', **params)

        self.graph.redraw()
#        self._plot_cache = [self.graph.plotcontainer.components 

    @on_trait_change('fits:[fit,filterstr,filter_outliers]')
    def _changed(self, obj, name, new):
        n = len(self.fits) - 1
        plotid = n - self.fits.index(obj)
        g = self.graph

        if name == 'fit':
            g.set_fit(new, plotid=plotid)
        elif name == 'filterstr':
            g.set_filter(new, plotid=plotid)
        elif name == 'filter_outliers':
            g.set_filter_outliers(new, plotid=plotid)

        self._suppress_update = True
        g._update_graph()
        self._suppress_update = False
        try:
            reg = g.regressors[plotid]
            obj._intercept = reg.predict(0)
            obj._error = reg.coefficient_errors[-1]

        except IndexError:
            obj._intercept = 0
            obj._error = 0

        self.analysis.age_dirty = True

    @on_trait_change('graph:graph:regression_results')
    def _update_values(self, new):
        if self._suppress_update:
            return

        if new:
            n = len(self.fits) - 1
            for i, fi in enumerate(self.fits):
                reg = new[n - i]
                if reg:
                    fi._intercept = reg.predict(0)
                    fi._error = reg.coefficient_errors[-1]

        self.analysis.age_dirty = True

    def traits_view(self):
        v = View(
                 Group(
                       Item('fits',
                            style='custom',
                            show_label=False,
                            editor=ListEditor(mutable=False,
                                                editor=InstanceEditor(),
                                                style='custom'
                                                )),
                       show_border=True,
                       label='{} Fits'.format(self.name)
                       )
                 )
        return v
#============= EOF =============================================
