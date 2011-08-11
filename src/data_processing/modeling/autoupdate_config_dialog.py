#============= enthought library imports =======================
from traits.api import HasTraits, Float
from traitsui.api import View

#============= standard library imports ========================

#============= local library imports  ==========================
class AutoupdateConfigDialog(HasTraits):
    tempoffset = Float
    timeoffset = Float

    def traits_view(self):
        v = View('tempoffset',
               'timeoffset',
               buttons = ['OK', 'Cancel']
               )
        return v
#============= views ===================================


#============= EOF ====================================
