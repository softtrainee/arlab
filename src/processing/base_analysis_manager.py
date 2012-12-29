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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from src.progress_dialog import MProgressDialog
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseAnalysisManager(HasTraits):
    def _load_analyses(self, ans):
        progress = self._open_progress(len(ans))
        for ai in ans:
            msg = 'loading {}'.format(ai.record_id)
            progress.change_message(msg)
            ai.load_age()
            progress.increment()

    def _open_progress(self, n):
        pd = MProgressDialog(max=n, size=(550, 15))
        pd.open()
        pd.center()
        return pd
#============= EOF =============================================
