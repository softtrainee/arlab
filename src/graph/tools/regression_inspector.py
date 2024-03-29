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
from src.graph.tools.info_inspector import InfoInspector, InfoOverlay
#============= standard library imports ========================
#============= local library imports  ==========================


class RegressionInspectorTool(InfoInspector):
#    def _build_metadata(self, xy):
#        d = dict(regressor=self.component.regressor)
#        return d

    def assemble_lines(self):
        reg = self.component.regressor
        lines = [reg.make_equation()]
        lines += map(str.strip, map(str, reg.tostring().split(',')))
        return lines

class RegressionInspectorOverlay(InfoOverlay):
    pass

#============= EOF =============================================
