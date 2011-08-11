#============= enthought library imports =======================
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from src.led.wxLED import wxLED
#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
class _LEDEditor(Editor):
    def init(self, parent):
        '''

        '''

        self.control = self._create_control(parent)
        self.value.on_trait_change(self.update_object, 'state')

    def update_object(self, object, name, new):
        '''

        '''
        if name == 'state':
            if self.control is not None:
                self.control.set_state(new)

    def update_editor(self):
        '''
        '''
        pass

    def _create_control(self, parent):
        '''

        '''
        panel = wxLED(parent)
        return panel

class LEDEditor(BasicEditorFactory):
    '''
        G{classtree}
    '''
    klass = _LEDEditor
#============= EOF ====================================
