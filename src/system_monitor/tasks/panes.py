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
from pyface.tasks.traits_dock_pane import TraitsDockPane
from traits.api import Instance, Property, Int
from traitsui.api import View, UItem, TabularEditor

#============= standard library imports ========================
#============= local library imports  ==========================
from traitsui.tabular_adapter import TabularAdapter
from src.processing.tasks.analysis_edit.panes import TablePane
from src.system_monitor.tasks.connection_spec import ConnectionSpec
from src.ui.custom_label_editor import CustomLabel
from src.processing.tasks.analysis_edit.adapters import UnknownsAdapter


class AnalysisAdapter(UnknownsAdapter):
    record_id_width=Int(80)
    sample_width=Int(80)
    age_width=Int(70)
    error_width=Int(60)
    tag_width=Int(50)
    
    font = 'arial 10'
    

class AnalysisPane(TablePane):
    name = 'Analyses'
    id = 'pychron.sys_mon.analyses'
    n = Property(depends_on='items')

    def _get_n(self):
        return 'N Runs = {:02n}'.format(len(self.items))

    def traits_view(self):
        v = View(
            CustomLabel('n', color='blue'),
            UItem('items',
                  editor=TabularEditor(
                           editable=False,
                           refresh='refresh_needed',
                           adapter=AnalysisAdapter())))
        return v


class ConnectionPane(TraitsDockPane):
    name = 'Connection'
    id = 'pychron.sys_mon.connection'

    conn_spec = Instance(ConnectionSpec)

    def traits_view(self):
        v = View(UItem('conn_spec', style='custom'))
        return v


#============= EOF =============================================
