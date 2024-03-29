#===============================================================================
# Copyright 2011 Jake Ross
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
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class HardwarePerspective(Perspective):
    '''
    '''
    name = 'Hardware'
    show_editor_area = False

    contents = [
              PerspectiveItem(id='hardware.devices',
                              width=0.65
                              ),
              PerspectiveItem(id='hardware.current_device',
                              width=0.45
                              ),

#              PerspectiveItem(id = 'extraction_line.canvas',
#                              width = 0.65
#                              ),
#              PerspectiveItem(id = 'extraction_line.explanation', position = 'left',
#                              relative_to = 'extraction_line.canvas',
#                              width = 0.35
#                              ),
              ]
#============= views ===================================
#============= EOF ====================================
