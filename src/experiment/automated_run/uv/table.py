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
from traits.api import HasTraits, List, Any, Event, Str
from traitsui.api import View, Item
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.automated_run.tabular_adapter import AutomatedRunSpecAdapter, \
    UVAutomatedRunSpecAdapter
from src.experiment.automated_run.table import AutomatedRunsTable
from src.experiment.automated_run.uv.spec import UVAutomatedRunSpec
#============= standard library imports ========================
#============= local library imports  ==========================

class UVAutomatedRunsTable(AutomatedRunsTable):
    klass = UVAutomatedRunSpec
    adapter_klass = UVAutomatedRunSpecAdapter

#============= EOF =============================================
