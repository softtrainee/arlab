#============= enthought library imports =======================
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================

class NewCanvasAction(Action):
    '''
        G{classtree}
    '''
    description = 'Create a new Canvas'
    name = 'New Canvas'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service('src.canvas.designer.canvas_manager.CanvasManager')
        manager.window = event.window
        manager.new_canvas()

class OpenCanvasAction(Action):
    '''
        G{classtree}
    '''
    description = 'Open Canvas'
    name = 'Open Canvas'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service('src.canvas.designer.canvas_manager.CanvasManager')
        manager.window = event.window
        manager.open()

#============= EOF ====================================
