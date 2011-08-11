'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================


#=============standard library imports ========================
#from OpenGL.GL import *
#from OpenGL.GLU import *
#from wx import Timer, EVT_TIMER
#=============local library imports  ==========================

from canvas3D import Canvas3D
class AnimationCanvas3D(Canvas3D):
    '''
        G{classtree}
    '''

    def __init__(self, panel):
        '''
            @type parent: C{str}
            @param parent:
        '''
        super(AnimationCanvas3D, self).__init__(panel)
        #self.Bind(EVT_TIMER, self.OnTimer)
        #self.t1 = Timer(self)
        #t = 1000.0 / 24
        #self.t1.Start(t)

    def OnTimer(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.scene_graph.increment_animation_counter()
#        if self.scene_graph.animate_cnt>100:
#            self.scene_graph.animate_cnt=0
#        
        self.Refresh()
