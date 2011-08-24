#============= enthought library imports =======================
from enable.component_editor import ComponentEditor, _ComponentEditor

#============= standard library imports ========================
from wx import EVT_KEY_UP

#============= local library imports  ==========================

class _LaserComponentEditor(_ComponentEditor):
    def init(self, parent):
        '''
        Finishes initializing the editor by creating the underlying toolkit
        widget.
   
        '''
        super(_LaserComponentEditor, self).init(parent)
        self.control.Bind(EVT_KEY_UP, self.onKeyUp)

    def onKeyUp(self, event):
        self.value.end_key(event)

class LaserComponentEditor(ComponentEditor):
    klass = _LaserComponentEditor

#============= EOF =============================================
