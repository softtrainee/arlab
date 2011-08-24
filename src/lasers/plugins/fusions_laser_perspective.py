#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class FusionsLaserPerspective(Perspective):
    name = 'Laser'
    show_editor_area = False
    w = 0.33
    h = 0.33
    contents = [PerspectiveItem(id = 'fusions.laser_control',
                                width = w,
                                ),
                PerspectiveItem(id = 'fusions.control_module',
                                width = w,
                                relative_to = 'fusions.laser_control',
                                position = 'bottom'
                                ),
                PerspectiveItem(id = 'fusions.stage',
                                width = 1 - w,
                                height = 1.0
                                )
                ]
#============= views ===================================
#============= EOF ====================================
