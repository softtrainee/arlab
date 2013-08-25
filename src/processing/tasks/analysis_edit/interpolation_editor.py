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
from traits.api import HasTraits, List, on_trait_change, Instance
from traitsui.api import View, Item
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor

#============= standard library imports ========================
from numpy import Inf
from src.processing.tasks.analysis_edit.fits import InterpolationFitSelector
#============= local library imports  ==========================


class InterpolationEditor(GraphEditor):
    tool = Instance(InterpolationFitSelector, ())
    references = List
    _references = List


    @on_trait_change('references[]')
    def _update_references(self):
        self.make_references()
        self.rebuild_graph()

    def make_references(self):
        self._references = self.processor.make_analyses(self.references)
        self.processor.load_analyses(self._references)
        self._make_references()

    def _make_references(self):
        pass

    def _get_start_end(self, rxs, uxs):
        mrxs = min(rxs) if rxs else Inf
        muxs = min(uxs) if uxs else Inf

        marxs = max(rxs) if rxs else -Inf
        mauxs = max(uxs) if uxs else -Inf

        start = min(mrxs, muxs)
        end = max(marxs, mauxs)
        return start, end
#============= EOF =============================================
