#============= enthought library imports =======================
from traits.api import Bool
#from enable.component_editor import ComponentEditor , _ComponentEditor
#============= standard library imports ========================
from wx import EVT_IDLE, EVT_PAINT, BufferedPaintDC
from src.managers.stage_managers.stage_component_editor import LaserComponentEditor, \
    _LaserComponentEditor
#============= local library imports  ==========================


class _VideoComponentEditor(_LaserComponentEditor):
    '''
    '''
    def init(self, parent):
        '''
        Finishes initializing the editor by creating the underlying toolkit
        widget.
   
        '''
        super(_VideoComponentEditor, self).init(parent)
        self.control.Bind(EVT_IDLE, self.onIdle)

#        print self.context_object, self.object, self.value

#        pause_canvas = False
#        if pause_canvas:
#            self.value.on_trait_change(self.update_editor_item,
#                                            'pause'
#                                            )
#    def update_editor_item(self, obj, name, old, new):
#        if isinstance(new, bool):
#            self.render = not new


    def onIdle(self, event):
        '''
      
        '''


        if self.control is not None:

            self.control.Refresh()

        #force  the control to refresh perodically rendering a smooth video stream
        event.RequestMore()

class VideoComponentEditor(LaserComponentEditor):
    '''
    '''
    klass = _VideoComponentEditor

#============= EOF ====================================
