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
from traits.api import List
from traitsui.api import View, Item, UItem, TabularEditor
from src.envisage.tasks.base_editor import BaseTraitsEditor
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
#============= local library imports  ==========================

class LaserTableAdapter(TabularAdapter):
    columns = [('RunID', 'record_id')]

class LaserTableEditor(BaseTraitsEditor):
    analyses = List
    def traits_view(self):
        v = View(UItem('analyses',
                       editor=TabularEditor(adapter=LaserTableAdapter(),
                                            editable=False
                                            )

                       ))
        return v
#============= EOF =============================================
