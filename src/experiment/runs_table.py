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
from traits.api import HasTraits, Any, List, Str
from traitsui.api import View, Item, TableEditor
from src.experiment.automated_run import AutomatedRun
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter, \
    UVAutomatedRunAdapter
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.uv_automated_run import UVAutomatedRun

#============= standard library imports ========================
#============= local library imports  ==========================

class RunsTable(HasTraits):
    automated_runs = List(AutomatedRun)
    selected = Any
    extract_device = Str
    def set_runs(self, runs):
        if runs:
            klass = AutomatedRun
            if self.extract_device == 'Fusions UV':
                klass = UVAutomatedRun

            for ri in runs:
                if ri.__class__ != klass:
                    nri = klass()
                    for di in ri.traits():
                        try:
                            setattr(nri, di, getattr(ri, di))
                        except Exception:
                            pass

                    ri = nri
                self.automated_runs.append(ri)

    def traits_view(self):
        tklass = AutomatedRunAdapter
        if self.extract_device == 'Fusions UV':
            tklass = UVAutomatedRunAdapter

        v = View(Item('automated_runs',
                      show_label=False,
                      editor=myTabularEditor(adapter=tklass(),
                                            operations=['delete',
                                                        'move',
#                                                                        'edit'
                                                        ],
                                            editable=False,
                                            selected='selected',
                                            auto_update=True,
                                            multi_select=True,
                                            scroll_to_bottom=False)
                      )
                 )
        return v
#============= EOF =============================================
