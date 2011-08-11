#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class ExtractionLinePerspective(Perspective):
    '''
        G{classtree}
    '''
    name = 'Extraction Line'
    show_editor_area = False

    contents = [

              PerspectiveItem(id = 'extraction_line.canvas',
                              width = 0.65
                              ),
              PerspectiveItem(id = 'extraction_line.explanation', position = 'left',
                              relative_to = 'extraction_line.canvas',
                              width = 0.35
                              ),
              ]
#============= views ===================================
#============= EOF ====================================
