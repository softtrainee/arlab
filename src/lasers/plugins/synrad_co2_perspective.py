#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class SynradCO2Perspective(Perspective):
    name = 'Synrad Laser'
    show_editor_area = False

    contents = [PerspectiveItem(id = 'synrad.control',
                                width = 0.75,
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
