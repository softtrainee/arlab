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
from traits.api import HasTraits, Any, Instance, on_trait_change, \
    List, Bool, Int, Float
from traitsui.api import View, Item, UItem
from enable.component_editor import ComponentEditor as EnableComponentEditor
#============= standard library imports ========================
from itertools import groupby
#============= local library imports  ==========================
from src.processing.plotter_options_manager import IdeogramOptionsManager, \
    SpectrumOptionsManager, InverseIsochronOptionsManager, SeriesOptionsManager
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
from src.codetools.simple_timeit import timethis


class FigureEditor(GraphEditor):
#     path = File
    component = Any
    plotter = Any
#     tool = Any
    plotter_options_manager = Any
#     processor = Any
#     unknowns = List
#     _unknowns = List
#     _cached_unknowns = List
    _suppress_rebuild = False
    def traits_view(self):
        v = View(UItem('component',
                       style='custom',
                       width=650,
                       editor=EnableComponentEditor()))
        return v

#     @on_trait_change('unknowns[]')
#     def _update_unknowns(self, new):
#         if not self._suppress_rebuild and new:
#             self.rebuild()

    def set_group(self, idxs, gid, refresh=True):
        for i, (ui, uu) in enumerate(zip(self._unknowns, self.unknowns)):
            if i in idxs:
                ui.group_id = gid
                uu.group_id = gid
        if refresh:
            self.rebuild(refresh_data=False)

    def _rebuild_graph(self):
        self.rebuild(refresh_data=False)

    def rebuild(self, refresh_data=True):
        ans = self._gather_unknowns(refresh_data)
        po = self.plotter_options_manager.plotter_options

        comp = timethis(self._get_component, args=(ans, po))
#         comp = self._get_component(ans, po)

        self.component = comp
        self.component_changed = True

#     def _gather_unknowns(self, refresh_data):
#         ans = self._unknowns
#         if refresh_data or not ans:
#             unks = self.processor.make_analyses(self.unknowns,
#                                                 calculate_age=False
#                                                 )
#             ans = unks
#
#             if ans:
#                 # compress groups
#                 self._compress_unknowns(ans)
#                 self._unknowns = ans
#
#         return ans
#
#     def _compress_unknowns(self, ans):
#         key = lambda x: x.group_id
#         ans = sorted(ans, key=key)
#         groups = groupby(ans, key)
#
#         mgid, analyses = groups.next()
#         for ai in analyses:
#             ai.group_id = 0
#
#         for gid, analyses in groups:
#             for ai in analyses:
#                 ai.group_id = gid - mgid

#     def _get_component(self, ans, po):
#         raise NotImplementedError
    def _get_component(self, ans, po):
        func = getattr(self.processor, self.func)
        return func(ans=ans, plotter_options=po)

#         if args:
#             retur
#             comp, plotter = args
#             self.plotter = plotter
#             return comp


class IdeogramEditor(FigureEditor):
    plotter_options_manager = Instance(IdeogramOptionsManager, ())
    func = 'new_ideogram'
#     def _get_component(self, ans, po):
#         args = self.processor.new_ideogram(ans=ans, plotter_options=po)
#         if args:
#             comp, plotter = args
#             self.plotter = plotter
#             return comp

class SpectrumEditor(FigureEditor):
    plotter_options_manager = Instance(SpectrumOptionsManager, ())
    func = 'new_spectrum'
#     def _get_component(self, ans, po):
#         comp, plotter = self.processor.new_spectrum(ans=ans, plotter_options=po)
#         self.plotter = plotter
#         return comp

class InverseIsochronEditor(FigureEditor):
    plotter_options_manager = Instance(InverseIsochronOptionsManager, ())
    def _get_component(self, ans, po):
        if ans:
            comp, plotter = self.processor.new_inverse_isochron(ans=ans, plotter_options=po)
            self.plotter = plotter
            return comp

class SeriesEditor(FigureEditor):
    plotter_options_manager = Instance(SeriesOptionsManager, ())
#     func = 'new_series'
#     plotter_options_manager = Instance(SeriesOptionsManager, ())
    def _get_component(self, ans, po):
        if ans:
            comp, plotter = self.processor.new_series(ans=ans,
                                                      options=dict(fits=self.tool.fits),
                                                      plotter_options=po)
            self.plotter = plotter
            return comp

    def show_series(self, key, fit='Linear'):
        fi = next((ti for ti in self.tool.fits if ti.name == key), None)
#         self.tool.suppress_refresh_unknowns = True
        if fi:
            fi.trait_set(
                         fit=fit,
                         show=True,
                         trait_change_notify=False)

        self.rebuild(refresh_data=False)
#             fi.fit = fit
#             fi.show = True

#         self.tool.suppress_refresh_unknowns = False

class AutoIdeogramControl(HasTraits):
    group_by_aliquot = Bool(False)
    group_by_labnumber = Bool(False)
    def traits_view(self):
        v = View(
                 Item('group_by_aliquot'),
                 Item('group_by_labnumber'),

                 )
        return v


class AutoSeriesControl(HasTraits):
    days = Int(1)
    hours = Float(0)
    def traits_view(self):
        v = View(
               Item('days'),
               Item('hours')
               )
        return v


class AutoIdeogramEditor(IdeogramEditor):
    auto_figure_control = Instance(AutoIdeogramControl, ())


class AutoSpectrumEditor(SpectrumEditor):
    auto_figure_control = Instance(AutoIdeogramControl, ())


class AutoSeriesEditor(SeriesEditor):
    auto_figure_control = Instance(AutoSeriesControl, ())



#============= EOF =============================================
#
#     def _gather_unknowns_cached(self):
#         if self._cached_unknowns:
#             # removed items:
# #             if len(self.unknowns) < len(self._cached_unknowns):
#             # added items
# #             else:
#
#             # get analyses not loaded
#             cached_recids = [ui.record_id for ui in self._cached_unknowns]
#             nonloaded = [ui for ui in self.unknowns
#                             if not ui.record_id in cached_recids]
#             if nonloaded:
#                 nonloaded = self.processor.make_analyses(nonloaded)
#                 self.processor.load_analyses(nonloaded)
#                 self._unknowns.extend(nonloaded)
#
#             # remove analyses in _unknowns but not in unknowns
#             recids = [ui.record_id for ui in self.unknowns]
#             ans = [ui for ui in  self._unknowns
#                    if ui.record_id in recids]
# #             for i,ci in enumerate(self._cached_unknowns):
# #                 if ci in self.unknowns:
# #             ans = self._unknowns
# #             ans = [ui for ui, ci in zip(self._unknowns, self._cached_unknowns)
# #                                     if ci in self.unknowns]
#         else:
#             unks = self.unknowns
#             unks = self.processor.make_analyses(unks)
#             self.processor.load_analyses(unks)
#             ans = unks
#
# #         self._cached_unknowns = self.unknowns[:]
#         if ans:
#
#             # compress groups
#             self._compress_unknowns(ans)
#
#             self._unknowns = ans
#             return ans
