'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import Any, Int
from chaco.tools.api import ScatterInspector

#=============standard library imports ========================

#=============local library imports  ==========================
class ScatterTool(ScatterInspector):
    '''
        G{classtree}
    '''
    parent = Any
    plotid = Int(0)
    def normal_mouse_move(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        #self.parent.selected_plotid = self.plotid
        #super(ScatterTool, self).normal_mouse_move(event)
        ScatterInspector.normal_mouse_move(self, event)