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
from traits.api import HasTraits, Instance
from traitsui.api import View, Item, VGroup, HGroup, InstanceEditor
from src.viewable import Viewable
from src.experiment.automated_run import AutomatedRun
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.script_editable import ScriptEditable
from src.constants import SCRIPT_KEYS

class AutomatedRunEditor(ScriptEditable):
    id = 'automated_run_editor'
    title = 'Edit Automated Runs'
    run = Instance(AutomatedRun)
    def commit_changes(self, runs):
        for ri in runs:
            for si in SCRIPT_KEYS:
                self._update_run_script(ri, si)
            ri.skip = self.run.skip


    def _run_changed(self):
        run = self.run
        self.mass_spectrometer = run.mass_spectrometer

        for si in SCRIPT_KEYS:
            sname = '{}_script'.format(si)
            sc = getattr(run, sname)
            if sc:
                n = self._clean_script_name(sc.name)
                setattr(self, sname, n)

    def traits_view(self):
#        v = VGroup(Item('extract_value'))
        g = VGroup(Item('run', show_label=False,
                        style='custom',
                        editor=InstanceEditor(view='simple_view')),
                   self._get_script_group()
                   )

        return self.view_factory(g, buttons=['OK', 'Cancel'])
#============= EOF =============================================
