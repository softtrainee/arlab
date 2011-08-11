'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import HasTraits, Str, Bool, Any, Property

#=============standard library imports ========================

#=============local library imports  ==========================
class ExplanableItem(HasTraits):
    '''
        G{classtree}
    '''
    name = Str
    state_property = Property(depends_on = 'state')
    state = Bool(False)
    description = Str
    identify = Bool(False)

    lock_property = Property(depends_on = 'soft_lock')
    soft_lock = Bool(False)

    canvas = Any

    def _get_lock_property(self):
        return 'Yes' if self.soft_lock else 'No'

    def _get_state_property(self):
        return 'Open' if self.state else 'Closed'

    def _identify_changed(self):
        '''
        '''
        self.canvas.toggle_item_identify(self.name)
        #self.canvas3D.toggle_item_identify(self.id)


class ExplanableTurbo(ExplanableItem):
    '''
        G{classtree}
    '''
    def _get_state_property(self):
        return 'On' if self.state else 'Off'

class ExplanableValve(ExplanableItem):
    '''
        G{classtree}
    '''
    pass
    #address = Str
    #interlocks = Str
    #auto = True

#    def _get_id(self):
#        '''
#        '''
#        return self.name

    # parent = None
#    def __init__(self, canvas, *args, **kw):
#        super(Valve, self).__init__()
#        self.name = args[0]
#        self.address = args[1]
#        self.state = args[2]
#        self.interlocks = args[3]
#        self.auto = args[4]
#        self.description = args[5]
#        self. = parent
        #canvas....
        #self.parent.identify_valve_by_name(self.name)
