#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Instance, Str, Bool, List, implements, on_trait_change, \
    Any, Event, Property
from traitsui.api import View, Item, UItem, ListEditor, InstanceEditor, \
    EnumEditor, HGroup, VGroup, spring, Label, Spring
from chaco.array_data_source import ArrayDataSource

#============= standard library imports ========================
from numpy import asarray, Inf
#============= local library imports  ==========================
from src.constants import FIT_TYPES
from src.processing.tasks.analysis_edit.ianalysis_edit_tool import IAnalysisEditTool
from src.graph.regression_graph import StackedRegressionGraph
from src.regression.interpolation_regressor import InterpolationRegressor
from src.regression.ols_regressor import OLSRegressor
from src.regression.mean_regressor import MeanRegressor
from src.helpers.datetime_tools import convert_timestamp
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
from src.processing.tasks.analysis_edit.interpolation_editor import InterpolationEditor
from src.helpers.isotope_utils import sort_isotopes

class BlanksEditor(InterpolationEditor):
    name = Str

    def save(self):

        if not any([si.valid for si in self.tool.fits]):
            return

        cname = 'blanks'
        self.info('Attempting to save corrections to database')

        for ui in self._unknowns:
            histories = getattr(ui.dbrecord, '{}_histories'.format(cname))
            phistory = histories[-1] if histories else None

            history = self.processor.add_history(ui, cname)
            for si in self.tool.fits:
                if not si.use:
                    self.debug('using previous value {} {}'.format(ui.record_id, si.name))
                    self.processor.apply_fixed_value_correction(phistory, history, si, cname)
                else:
                    self.debug('saving {} {}'.format(ui.record_id, si.name))
                    self.processor.apply_correction(history, ui, si, self._references, cname)

    @on_trait_change('graph:regression_results')
    def _update_regression(self, new):
        gen = self._graph_generator()
        for i, (fit, reg) in enumerate(zip(gen, new)):
            iso = fit.name
            plotobj = self.graph.plots[i]
            scatter = plotobj.plots['Unknowns-predicted'][0]
            xs = scatter.index.get_data()

            p_uys, p_ues = self._set_interpolated_values(iso, reg, xs)
            scatter.value.set_data(p_uys)
            scatter.yerror.set_data(p_ues)

    def _set_interpolated_values(self, iso, reg, xs):
        p_uys = reg.predict(xs)
        p_ues = reg.predict_error(xs)

        for ui, v, e in zip(self._unknowns, p_uys, p_ues):
            ui.set_blank(iso, v, e)
        return p_uys, p_ues

    def _rebuild_graph(self):
        graph = self.graph

        uxs = [ui.timestamp for ui in self._unknowns]
        rxs = [ui.timestamp for ui in self._references]

        display_xs = asarray(map(convert_timestamp, rxs[:]))

        start, end = self._get_start_end(rxs, uxs)

        c_uxs = self.normalize(uxs, start)
        r_xs = self.normalize(rxs, start)

        def get_isotope(ui, k, kind=None):
            if k in ui.isotopes:
                v = ui.isotopes[k]
                if kind is not None:
                    v = getattr(v, kind)
                v = v.value, v.error
            else:
                v = 0, 0
            return v

        '''
            c_... current value
            r... reference value
            p_... predicted value
        '''
        set_x_flag = False
        i = 0
        gen = self._graph_generator()
        for fit in gen:
            iso = fit.name
            set_x_flag = True
            fit = fit.fit.lower()
            c_uys, c_ues = None, None
            if self._unknowns:
                c_uys, c_ues = zip(*[get_isotope(ui, iso, 'blank')
                            for ui in self._unknowns
                            ])

            r_ys, r_es = None, None
            if self._references:
                r_ys, r_es = zip(*[get_isotope(ui, iso)
                            for ui in self._references
                            ])

            p = graph.new_plot(
                               ytitle=iso,
                               xtitle='Time (hrs)',
                               padding=[60, 10, 10, 60],
                               show_legend='ur'
                               )
            p.value_range.tight_bounds = False

            if c_ues and c_uys:
                # plot unknowns
                graph.new_series(c_uxs, c_uys,
                                 yerror=c_ues,
                                 fit=False,
                                 type='scatter',
                                 plotid=i
                                 )
                graph.set_series_label('Unknowns-Current', plotid=i)

            if r_es and r_ys:
                # plot references
                if fit in ['preceeding', 'bracketing interpolate', 'bracketing average']:
                    reg = InterpolationRegressor(xs=r_xs,
                                                 ys=r_ys,
                                                 yserr=r_es,
                                                 kind=fit)
                    scatter, _p = graph.new_series(r_xs, r_ys,
                                 yerror=r_es,
                                 type='scatter',
                                 plotid=i,
                                 fit=False
                                 )

                else:
                    _p, scatter, l = graph.new_series(r_xs, r_ys,
                                       display_index=ArrayDataSource(data=display_xs),
                                       yerror=ArrayDataSource(data=r_es),
                                       fit=fit,
                                       plotid=i)
                    reg = l.regressor
#                    if fit.startswith('average'):
#                        reg2 = MeanRegressor(xs=r_xs, ys=r_ys, yserr=r_es)
#                    else:
#                        reg2 = OLSRegressor(xs=r_xs, ys=r_ys, yserr=r_es, fit=fit)

#                p_uys = reg.predict(c_uxs)
#                p_ues = reg.predict_error(c_uxs)
#
#                for ui, v, e in zip(self._unknowns, p_uys, p_ues):
#                    ui.set_blank(iso, v, e)
#                        ui.blank.value = v
#                        ui.blank.error = e
                p_uys, p_ues = self._set_interpolated_values(iso, reg, c_uxs)
                # display the predicted values
                ss, _ = graph.new_series(c_uxs,
                                         p_uys,
                                         isotope=iso,
                                         yerror=ArrayDataSource(p_ues),
                                         fit=False,
                                         type='scatter',
                                         plotid=i,
                                         )
                graph.set_series_label('Unknowns-predicted', plotid=i)
            i += 1

        if set_x_flag:
            m = (end - start) / 3600.
            graph.set_x_limits(0, m, pad='0.1')
            graph.refresh()

    def _make_references(self):

        keys = set([ki  for ui in self._references
                        for ki in ui.isotope_keys])
        keys = sort_isotopes(keys)

        self.tool.load_fits(keys)

    def _graph_default(self):
        return StackedRegressionGraph(container_dict=dict(stack_order='top_to_bottom'))


#============= EOF =============================================
