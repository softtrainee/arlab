#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class GraphPerspective(Perspective):
    '''
        G{classtree}
    '''
    name = 'Graph'
    show_editor_area = True

    contents = [
                PerspectiveItem(id = 'pychron.graph_manager',
                              #width = 0.65
                              )
              ]
#              PerspectiveItem(id = 'hardware.devices',
#                              width = 0.65
#                              ),
#              PerspectiveItem(id = 'hardware.current_device',
#                              width = 0.45
#                              ),

#              PerspectiveItem(id = 'extraction_line.canvas',
#                              width = 0.65
#                              ),
#              PerspectiveItem(id = 'extraction_line.explanation', position = 'left',
#                              relative_to = 'extraction_line.canvas',
#                              width = 0.35
#                              ),
#              ]
#============= views ===================================
#============= EOF ====================================
