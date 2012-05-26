#===============================================================================
# Copyright 2011 Jake Ross
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



#=============enthought library imports=======================
from traits.api import Str, Bool

#============= standard library imports ========================

#============= local library imports  ==========================
from src.graph.editors.series_editor import SeriesEditor, PolygonPlotEditor, \
    ContourPolyPlotEditor


class DiffusionSeriesEditor(SeriesEditor):
    runid = Str
    show_sample = Bool(True)
    show_model = Bool(True)
    show_inverse_model = Bool(True)
    isspectrum = Bool(False)
    iscoolinghistory = Bool(False)

    def _show_inverse_model_changed(self):
        if self.isspectrum:
            try:
                plots = self.graph.groups['inverse_model_spectrum']
            except KeyError:
                return
            for p in plots:
                p = p[0]
                p.visible = self.show_inverse_model

            self.graph.redraw()

    def _show_sample_changed(self):
        if self.isspectrum:
            #toggles visibility of the error envelope
            self.graph.set_series_visiblity(self.show_sample, plotid=self.plotid,
                                            series='{}.meas-err'.format(self.runid))

        self.graph.set_series_visiblity(self.show_sample, plotid=self.plotid,
                                        series='{}.meas'.format(self.runid))

    def _show_model_changed(self):
        self.graph.set_series_visiblity(self.show_model, plotid=self.plotid,
                                        series='{}.model'.format(self.runid))


class PolyDiffusionSeriesEditor(PolygonPlotEditor, DiffusionSeriesEditor):
    pass


class ContourPolyDiffusionSeriesEditor(ContourPolyPlotEditor, DiffusionSeriesEditor):
    pass
#============= EOF =====================================
