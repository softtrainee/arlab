#=============enthought library imports=======================
from enable.api import Component, Pointer

#=============standard library imports ========================

#=============local library imports  ==========================
class BaseCanvas(Component):
    '''
        G{classtree}
    '''
    #directory = None
    select_pointer = Pointer('hand')
    normal_pointer = Pointer('arrow')