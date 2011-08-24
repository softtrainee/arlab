#============= enthought library imports =======================
from traits.api import HasTraits, Bool, Property, Str, Any


#============= standard library imports ========================
import os
#============= local library imports  ==========================

#============= views ===================================
class ModelDataDirectory(HasTraits):
    '''
        G{classtree}
    '''
    show = Bool
    bind = Bool
    name = Property(depends_on = 'path')
    path = Str
    id = 0
    modeler = Any
    def _get_name(self):
        '''
        '''
        return os.path.basename(self.path)

    def _show_changed(self):
        '''
        '''
        if self.modeler:
            self.modeler.graph.set_group_visiblity(self.show, gid = self.id)
            self.modeler.update_graph_title()


    def _bind_changed(self):
        '''
        '''
        if self.modeler:
            self.modeler.graph.set_group_binding(self.id, self.bind)

#============= EOF ====================================
