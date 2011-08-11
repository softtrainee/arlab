#============= enthought library imports =======================
from traits.api import HasTraits, Int, Property

#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
COLORS = ['red', 'yellow', 'green', 'black']
class LED(HasTraits):
    '''
        G{classtree}
    '''
    state = Property(depends_on = '_state')
    _state = Int
    def _set_state(self, v):
        if isinstance(v, str):
            self._state = COLORS.index(v)
        else:
            self._state = v

    def _get_state(self):
        return self._state



#============= EOF ====================================
