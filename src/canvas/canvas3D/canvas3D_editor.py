#============= enthought library imports =======================
from traits.api import Any #, Float, Bool, List
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory

#============= standard library imports ========================
#from wx import Panel
#============= local library imports  ==========================

class _Canvas3DEditor(Editor):
    '''
        G{classtree}
    '''
    manager = Any
    def init(self, parent):
        '''
            @type parent: C{str}
            @param parent:
        '''
        self.control = self._create_control(parent)

    def _create_control(self, parent):
        '''
            @type parent: C{str}
            @param parent:
        '''
        from extraction_line_canvas3D import ExtractionLineCanvas3D
        panel = ExtractionLineCanvas3D(parent, self.object.manager)
        panel.setup()
        self.object.canvas3D.canvas = panel

        return panel

    def update_editor(self):
        '''
        '''
        self.control.Refresh()

class Canvas3DEditor(BasicEditorFactory):
    '''
        G{classtree}
    '''
    klass = _Canvas3DEditor
#============= EOF ====================================
