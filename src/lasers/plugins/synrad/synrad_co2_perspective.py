'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class SynradCO2Perspective(Perspective):
    name = 'Synrad Laser'
    show_editor_area = False

    contents = [PerspectiveItem(id='synrad.control',
                                width=0.75,
                                ),
#                PerspectiveItem(id = 'fusions.control_module',
#                                width = w,
#                                relative_to = 'fusions.laser_control',
#                                position = 'bottom'
#                                ),
#                PerspectiveItem(id = 'fusions.stage',
#                                width = 1 - w,
#                                height = 1.0
#                                )
                ]
#============= views ===================================
#============= EOF ====================================
