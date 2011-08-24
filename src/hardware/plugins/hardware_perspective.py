#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class HardwarePerspective(Perspective):
    '''
        G{classtree}
    '''
    name = 'Hardware'
    show_editor_area = False

    contents = [
              PerspectiveItem(id = 'hardware.devices',
                              width = 0.65
                              ),
              PerspectiveItem(id = 'hardware.current_device',
                              width = 0.45
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
