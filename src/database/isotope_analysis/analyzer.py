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
from traits.api import HasTraits, List, Instance, Any, on_trait_change
from traitsui.api import View, Item, ListEditor, InstanceEditor
from analysis_parameters import AnalysisParameters
#============= standard library imports ========================
#============= local library imports  ==========================
class Analyzer(HasTraits):
    analysis = Any
    fits = List(Instance(AnalysisParameters, ()))
    def _analysis_changed(self):
        keys = list(self.analysis.iso_keys)
        keys.reverse()
        g = self.analysis.signal_graph
        n = len(keys) - 1
        self.fits = [AnalysisParameters(fit='linear',
                                        graph=g,
                                        analyzer=self,
                                        intercept=g.get_intercept(n - i),
                                        name=k) for i, k in enumerate(keys)]


    @on_trait_change('fits:fit, fits:filterstr')
    def _changed(self, obj, name, new):

        if name == 'fit':
            attr = 'fit_types'
#            trim = 3
        else:
            attr = 'filters'
#            trim = 6

        plotid = list(self.analysis.iso_keys).index(obj.name)
        g = self.analysis.signal_graph
        getattr(g, attr)[plotid] = new

        g.regress_plots()
        obj.intercept = g.get_intercept(plotid)

    def traits_view(self):
        v = View(Item('fits',
                      style='custom',
                      show_label=False,
                      editor=ListEditor(mutable=False,
                                                editor=InstanceEditor(),
                                                style='custom'
                                                )))
        return v
#============= EOF =============================================
