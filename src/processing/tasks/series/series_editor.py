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
# from traits.api import HasTraits
# from traitsui.api import View, Item
# from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
#============= standard library imports ========================
#============= local library imports  ==========================

# class SeriesEditor(GraphEditor):
#
#     def _rebuild_graph(self):
#         g = self.graph
#
#         xs = [ui.timestamp for ui in self._unknowns]
#         xs = self.normalize(xs)
#         set_x_flag = False
#         i = 0
#         for fit in self.tool.fits:
#             if fit.fit and fit.show:
#                 iso = fit.name
#                 set_x_flag = True
#                 p = g.new_plot(xtitle='Time',
#                                ytitle='{} (fA)'.format(iso)
#                                )
#
#                 isos = [ui.isotopes[iso] for ui in self._unknowns]
#                 ys = [iso.value for iso in isos]
#                 g.new_series(xs, ys,
#                              type='scatter',
#                              plotid=i,
#                              fit=fit.fit
#                              )
#                 i += 1
#
#         if set_x_flag:
#             g.set_x_limits(0, max(xs), pad='0.1')
#             g.refresh()


#============= EOF =============================================
