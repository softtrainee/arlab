# @PydevCodeAnalysisIgnore
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
from traits.api import Instance, on_trait_change, Bool
from traitsui.api import Item, VGroup
from src.processing.analysis import AnalysisTabularAdapter

#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.plotters.api import Ideogram, InverseIsochron, Spectrum
from src.processing.series.blanks_editor import BlanksEditor
from src.processing.figures.base_figure import BaseFigure, GraphSelector
# from src.processing.result import Result
from src.helpers.traitsui_shortcuts import instance_item
from src.processing.series.backgrounds_editor import BackgroundsEditor
from src.processing.series.detector_intercalibration_editor import DetectorIntercalibrationEditor

class FigureGraphSelector(GraphSelector):
    show_ideo = Bool(True)
    show_inverse_isochron = Bool(False)
    show_spectrum = Bool(False)

    def _get_selections(self):
        s = super(FigureGraphSelector, self)._get_selections()
        return s + [    Item('show_ideo', label='Ideogram'),
                        Item('show_inverse_isochron', label='Inv. Isochron'),
                        Item('show_spectrum', label='Spectrum')
                        ]

class Figure(BaseFigure):
    ideogram = Instance(Ideogram)
    _cached_ideogram = Instance(Ideogram)
    spectrum = Instance(Spectrum)
    inverse_isochron = Instance(InverseIsochron)

    graph_selector = Instance(FigureGraphSelector, ())
    blanks_editor = Instance(BlanksEditor)
    backgrounds_editor = Instance(BackgroundsEditor)
    detector_intercalibration_editor = Instance(DetectorIntercalibrationEditor)
    nanalyses = -1

    def _refresh(self, graph, analyses, padding):

#        self.result = Result()
#        result = self.result

#        pl = 70 if self.show_series else 40
#        padding = [pl, 10, 0, 30]
        specpadding = padding
        ideopadding = padding
        isopadding = padding
#        seriespadding = padding
        gs = self.graph_selector
        if gs.show_ideo:
            '''
                need to do self.ig for .on_trait_change to work
            '''
#            print self._cached_ideogram
            if self._cached_ideogram is not None:
                self.ideogram = ideo = self._cached_ideogram
            else:
                self.ideogram = ideo = Ideogram(db=self.db)

            ideo.figure = self
            ideo.on_trait_change(self._update_selected_analysis, 'selected_analysis')
            ideo.on_trait_change(self.refresh, 'ideogram_of_means')

            gideo = ideo.build(analyses, padding=ideopadding)
            if gideo:
                gideo, plots = gideo
#                graph.plotcontainer.add(gideo.plotcontainer)
#                graph.plotcontainer.add(gideo)
                graph.add(gideo)
#                graph.plots += plots
            self._cached_ideogram = ideo
#                result.add(ig)
        else:
            if self.ideogram:
                self._cached_ideogram = self.ideogram.clone_traits()

            del self.ideogram

        if gs.show_spectrum:
            spec = self.spectrum
            if spec is None:
                spec = Spectrum()
                self.spectrum = spec
            gspec = spec.build(analyses, padding=specpadding)
            if gspec:
#                graph.plotcontainer.add(gspec.plotcontainer)
                graph.add(gspec.plotcontainer)
        else:
            del self.spectrum

        if gs.show_inverse_isochron:
            isochron = self.inverse_isochron
            if isochron is None:
                isochron = InverseIsochron()
                self.inverse_isochron = isochron
            giso = isochron.build(analyses, padding=isopadding)
            if giso:
                graph.add(giso.plotcontainer)
        else:
            del self.inverse_isochron

        super(Figure, self)._refresh(graph, analyses, padding)

    def load_analyses(self, *args, **kw):
        super(Figure, self).load_analyses(*args, **kw)
        self.blanks_editor = BlanksEditor(db=self.db,
                                          figure=self
                                          )
        isos = self.isotope_keys[:]
        isos.reverse()
        self.blanks_editor.add(isos)

        self.backgrounds_editor = BackgroundsEditor(db=self.db,
                                          figure=self
                                          )
        self.backgrounds_editor.add(isos)

        self.detector_intercalibration_editor = DetectorIntercalibrationEditor(db=self.db,
                                                                               figure=self)
        self.detector_intercalibration_editor.add(['IC'])

#        keys = self.signal_keys
#        bl_keys = [i for i in keys if i.endswith('bl')]
#        bg_keys = [i for i in keys if i.endswith('bg')]

#        self.blank_table_adapter.iso_keys = bl_keys
#        self.background_table_adapter.iso_keys = bg_keys


#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('analyses:age_dirty,graph_selector:show_+')
    def _refresh_graph(self, obj, name, old, new):
#        print name
        self.refresh(caller='figure._refresh_graph')

#===============================================================================
# views
#===============================================================================


    def _get_bottom_group(self):
        grp = super(Figure, self)._get_bottom_group()

#        blanksgrp , ta = self._analyses_table_factroy('Blanks')
#        self.blank_table_adapter = ta
#
#        grp.content.append(blanksgrp)
#
#        backsgrp, ta = self._analyses_table_factroy('Backgrounds')
#        self.background_table_adapter = ta
#        grp.content.append(backsgrp)

        height = 200
        editblankgrp = VGroup(
                              Item('blanks_editor',
                                   height=height,
                                   show_label=False, style='custom'),
#                              visible_when='blanks_editor',
                              label='Edit Blanks')

        editbackgrp = VGroup(
                              Item('backgrounds_editor',
                                   height=height,
                                   show_label=False, style='custom'),
#                              visible_when='backgrounds_editor',
                              label='Edit Backgrounds')
        editdetintergrp = VGroup(
                              Item('detector_intercalibration_editor',
                                   height=height,
                                   show_label=False, style='custom'),
#                              visible_when='detector_intercalibration_editor',
                              label='Edit Det. Intercal.')

        editideogrp = VGroup(
                             instance_item('ideogram', height=height),
                             visible_when='ideogram',
                             label='Edit Ideo.')
        editinvisogrp = VGroup(
                             instance_item('inverse_isochron', height=height),
                             visible_when='inverse_isochron',
                             label='Edit Inv. Isochron')
        editspecgrp = VGroup(
                             instance_item('spectrum', height=height),
                             visible_when='spectrum',
                             label='Edit Spectrum.')

        grp.content.append(editdetintergrp)
        grp.content.append(editblankgrp)
        grp.content.append(editbackgrp)
        grp.content.append(editideogrp)
        grp.content.append(editinvisogrp)
        grp.content.append(editspecgrp)

        return grp

#============= EOF =============================================
