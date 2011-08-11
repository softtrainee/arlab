#============= enthought library imports =======================
from traits.api import HasTraits, Bool, String, Float, Property
from traitsui.api import View, Item, HGroup

#============= standard library imports ========================

#============= local library imports  ==========================
class Valve(HasTraits):
    '''
        G{classtree}
    '''
    pos = Property(depends_on = '_x,_y')
    _x = Float(enter_set = True, auto_set = False)
    _y = Float(enter_set = True, auto_set = False)
    name = String
    state = Bool
    identify = Bool
    selected = Bool
    def _get_pos(self):
        '''
        '''
        return self._x, self._y

    def _set_pos(self, pos):
        '''
            @type pos: C{str}
            @param pos:
        '''
        self._x = float(pos[0])
        self._y = float(pos[1])

    def traits_view(self):
        '''
        '''
        return View('name', 'identify',
                     HGroup(Item('_x', format_str = '%0.2f'), Item('_y', format_str = '%0.2f')),
                    buttons = ['OK', 'Cancel']
                                 )
#============= views ===================================
#============= EOF ====================================
