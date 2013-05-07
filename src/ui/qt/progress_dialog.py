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
from pyface.api import ProgressDialog

#============= standard library imports ========================
from PySide.QtCore import QRect, QPoint, QSize
#============= local library imports  ==========================

class MProgressDialog(ProgressDialog):
    show_percent = True

    def get_value(self):
        if self.progress_bar:
            return self.progress_bar.value()
        else:
            return 0

    def increment(self, step=1):
        v = self.get_value()
        self.update(v + step)
#        time.sleep(1)

    def increase_max(self, step=1):
        self.max += step

    def set_size(self, w, h):
        self.dialog_size = QRect(QPoint(0, 0), QSize(w, h))
#============= EOF =============================================
