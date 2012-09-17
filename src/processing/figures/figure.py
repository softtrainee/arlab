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
from traitsui.api import Item, Group, VGroup
from src.processing.analysis import AnalysisTabularAdapter
from traitsui.editors.tabular_editor import TabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.plotters.api import Ideogram, InverseIsochron, Spectrum
from src.processing.blanks_editor import BlanksEditor
from src.processing.figures.base_figure import BaseFigure
from src.processing.result import Result
from src.helpers.traitsui_shortcuts import instance_item

class Figure(BaseFigure):

    ideogram = Instance(Ideogram)
    spectrum = Instance(Spectrum)
    inverse_isochron = Instance(InverseIsochron)

    blanks_editor = Instance(BlanksEditor)
    nanalyses = -1

    show_ideo = Bool(True)
#    show_isochron = Bool(True)
#    show_spectrum = Bool(True)

#    show_ideo = Bool(False)
    show_isochron = Bool(False)
    show_spectrum = Bool(False)
#    show_series = Bool(True)
    def _get_graph_shows(self):
        return [
                Item('show_series', label='Series'),
                Item('show_ideo', label='Ideogram'),
                Item('show_isochron', label='Isochron'),
                Item('show_spectrum', label='Spectrum')
                ]

    def _refresh(self, graph, analyses, padding):

#        self.result = Result()
#        result = self.result

#        pl = 70 if self.show_series else 40
#        padding = [pl, 10, 0, 30]
        specpadding = padding
        ideopadding = padding
        isopadding = padding
#        seriespadding = padding

        if self.show_ideo:
            '''
                need to do self.ig for .on_trait_change to work
            '''
            self.ideogram = ig = Ideogram()
            ig.on_trait_change(self._update_selected_analysis, 'selected_analysis')

            gideo = ig.build(analyses, padding=ideopadding)
            if gideo:
                graph.plotcontainer.add(gideo.plotcontainer)
#                result.add(ig)
        else:
            self.ideogram = None

        if self.show_spectrum:
            spectrum = Spectrum()
            gspec = spectrum.build(analyses, padding=specpadding)
            if gspec:
                graph.plotcontainer.add(gspec.plotcontainer)

        if self.show_isochron:
            isochron = InverseIsochron()
            giso = isochron.build(analyses, padding=isopadding)
            if giso:
                graph.plotcontainer.add(giso.plotcontainer)

        super(Figure, self)._refresh(graph, analyses, padding)

    def load_analyses(self, *args, **kw):
        super(Figure, self).load_analyses(*args, **kw)
        self.blanks_editor = BlanksEditor(db=self.db,
                                          workspace=self.workspace,
                                          repo=self.repo,
                                          analyses=self.analyses)

        keys = self.signal_keys
        bl_keys = [i for i in keys if i.endswith('bl')]
        bl_keys.sort(key=lambda k:k[2:4], reverse=True)

        self.blank_table_adapter.iso_keys = bl_keys
        self.blanks_editor.add(self.isotope_keys)

#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('analyses:age_dirty,show_ideo,show_isochron,show_spectrum')
    def _refresh_graph(self, obj, name, old, new):
        self.refresh()

#===============================================================================
# views
#===============================================================================
    def _get_bottom_group(self):
        grp = super(Figure, self)._get_bottom_group()

        self.blank_table_adapter = ta = AnalysisTabularAdapter()
        blanksgrp = Group(Item('analyses',
                                 show_label=False,
                                 height=0.3,
                                 editor=TabularEditor(adapter=ta,
                                           editable=False,
                                           )
                       ),
                       label='Blanks',
                       )

        grp.content.append(blanksgrp)

        editblankgrp = VGroup(
                              Item('blanks_editor',
                                   height=200,
                                   show_label=False, style='custom'),
                              visible_when='blanks_editor',
                              label='Edit Blanks')
        editideogrp = VGroup(
                             instance_item('ideogram', height=200),
                             visible_when='ideogram',
                             label='Edit Ideo.')

        grp.content.append(editblankgrp)
        grp.content.append(editideogrp)

        return grp

#============= EOF =============================================
