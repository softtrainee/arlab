#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class ScriptPerspective(Perspective):
    '''
        G{classtree}
    '''
    name = 'Script'
    show_editor_area = True

    contents = [
              PerspectiveItem(id = 'pychron.process_view'),
              PerspectiveItem(id = 'script.errors', position = 'bottom', relative_to = 'pychron.process_view'),
              ]
#============= views ===================================
#============= EOF ====================================
