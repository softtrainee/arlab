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
from src.experiment.automated_run.spec import AutomatedRunSpec
#============= standard library imports ========================
#============= local library imports  ==========================

class AutomatedRunsTable(HasTraits):
    automated_runs = List(AutomatedRunSpec)
    selected = Any
    rearranged = Event
    pasted = Event
    copy_cache = List
    update_needed = Event
    extract_device = Str
    klass = AutomatedRunSpec
    adapter_klass = AutomatedRunSpecAdapter

    def set_runs(self, runs):
        if runs:
            klass = self.klass
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
        v = View(Item('automated_runs',
                      show_label=False,
                      editor=myTabularEditor(adapter=self.adapter_klass(),
                                            operations=['delete',
                                                        'move',
#                                                        'edit'
                                                        ],
                                            editable=False,
                                            selected='selected',
                                            rearranged='rearranged',
                                            pasted='pasted',
                                            copy_cache='copy_cache',
                                            update='update_needed',
                                            auto_update=True,
                                            multi_select=True,
                                            scroll_to_bottom=False)
                      )
                 )
        return v
        return v
#============= EOF =============================================
