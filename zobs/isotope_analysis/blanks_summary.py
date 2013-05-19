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
# from traits.api import HasTraits, List, Str, Instance, Property, \
#     on_trait_change
# from traitsui.api import View, Item, ListStrEditor, HGroup
#============= standard library imports ========================
# import numpy as np
#============= local library imports  ==========================
# from src.database.isotope_analysis.summary import Summary
from src.database.isotope_analysis.history_summary import HistorySummary
# from src.graph.graph import Graph
# from src.graph.stacked_graph import StackedGraph

class BlanksSummary(HistorySummary):
    history_name = 'blanks'
    apply_name = 'selected_blanks'


#============= EOF =============================================
