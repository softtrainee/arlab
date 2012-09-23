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
from traits.api import HasTraits, Bool, Str, Enum, on_trait_change, Any, Property, Int
from traitsui.api import View, Item, HGroup, EnumEditor, spring
#============= standard library imports ========================
#============= local library imports  ==========================

class SeriesConfig(HasTraits):
    label = Str
    show = Bool
    show_baseline = Bool

    fit = Str('---')
    fits = Property

    fit_baseline = Enum('---', 'Linear', 'Parabolic', 'Cubic',
                        'Average ' + u'\u00b1SD',
                        'Average ' + u'\u00b1SEM',

                        )
    parent = Any(transient=True)
    stats = Str
    graphid = Int(0)

    def _get_fits(self):
        return ['---', 'Linear', 'Parabolic', 'Cubic',
                'Average ' + u'\u00b1SD',
                'Average ' + u'\u00b1SEM', ]

    @on_trait_change('show,show_baseline,fit,fit_baseline')
    def _change(self):
        if self.parent:
            self.parent.refresh()
#            if self.parent.series:
#                reg = self.parent.series.graph.regressors[self.graphid]
#            else:
#                return
#
#            if reg:
###                print reg.summary
###                print reg._result.pvalues
#                try:
##                    print reg.coefficients
#                    cs = reg.coefficients
#                    xx = ['', 'x', 'x2', 'x3']
#                    ss = '+ '.join(map(lambda x:'{:0.7f}{}'.format(*x),
#                                              zip(cs, xx[:len(cs)][::-1])))
##
#                    self.parent.results_display.add_text('\n')
#                    self.parent.results_display.add_text(ss)
##                    self.stats = ss
###                    ei = reg.coefficient_errors[-1]
###                    ei = rdict['coeff_errors'][-1]
###                    print rdict['coeff_errors']
###                    ii = rdict['coefficients'][-1]
###                    s = u'\u00b1' + '{:0.5f}'.format(ei)
###                    self.stats = s
#                except Exception, e:
#                    s = ''
#                    print e

    def traits_view(self):
        v = View(HGroup(Item('show', label=self.label),
                        Item('fit', editor=EnumEditor(name='fits'), show_label=False),
                        Item('show_baseline', label='Baseline'),
                        Item('fit_baseline', show_label=False),
                        spring,
                        Item('stats',
                             width=200,
                             show_label=False, style='readonly')
                        )
                 )
        return v
#============= EOF =============================================
