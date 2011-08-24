#============= enthought library imports =======================
from pyface.workbench.api import Perspective, PerspectiveItem

#============= standard library imports ========================

#============= local library imports  ==========================
class DatabasePerspective(Perspective):
    '''
        G{classtree}
    '''
    name = 'Database'
    show_editor_area = True

    contents = [
              PerspectiveItem(id = 'db.user'),
              PerspectiveItem(id = 'db.project', position = 'bottom', relative_to = 'db.user'),
              PerspectiveItem(id = 'db.sample', position = 'bottom', relative_to = 'db.project'),
              ]
#============= views ===================================
#============= EOF ====================================
