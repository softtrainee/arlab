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
    def _analysis_changed(self):
        if self.analysis:
            if self.analysis.isotope_keys:
                keys = list(self.analysis.isotope_keys)

                key = lambda x: re.sub('\D', '', x)
                keys = sorted(keys, key=key, reverse=True)

                n = len(keys) - 1
                self.fits = list(map(lambda x:self._param_factory(n, x), enumerate(keys)))

    def _param_factory(self, n, arg):

        i, name = arg
        reg = self.graph.regressors[n - i]
        fit = reg.fit
        if fit == 'average':
            fit = u'average \u00b1' + reg.error_calc.upper()

        obj = AnalysisParameters(name=name,
                                 fit=fit,
                                 intercept=reg.predict(0),
                                 error=reg.coefficient_errors[-1],
                                 )
        return obj

    @on_trait_change('fits:fit, fits:filterstr')
    def _changed(self, obj, name, new):
        n = len(self.fits) - 1
        plotid = n - self.fits.index(obj)
        g = self.graph
        if name == 'fit':
            g.set_fit(new, plotid=plotid)
        else:
            g.set_filter(new, plotid=plotid)

        self._suppress_update = True
        g._update_graph()
        self._suppress_update = False
        try:
            reg = g.regressors[plotid]
            obj.intercept = reg.predict(0)
            obj.error = reg.coefficient_errors[-1]
        except IndexError:
            obj.intercept = 0
            obj.error = 0

        self.analysis.age_dirty = True

    @on_trait_change('graph:graph:regression_results')
    def _update_values(self, new):
        if self._suppress_update:
            return

        if new:
            n = len(self.fits) - 1
            for i, fi in enumerate(self.fits):
                reg = new[n - i]
                fi.intercept = reg.predict(0)
                fi.error = reg.coefficient_errors[-1]
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
