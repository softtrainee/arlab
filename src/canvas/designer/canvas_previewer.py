#============= enthought library imports =======================
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from enable.component_editor import ComponentEditor

#============= standard library imports ========================

#============= local library imports  ==========================
from src.canvas.canvas2D.extraction_line_canvas2D import ExtractionLineCanvas2D
class CanvasPreviewer(HasTraits):
    '''
        G{classtree}
    '''
    canvas = Instance(ExtractionLineCanvas2D)
    def _canvas_default(self):
        '''
        '''
        return ExtractionLineCanvas2D()
    def traits_view(self):
        '''
        '''
        v = View(Item('canvas', editor = ComponentEditor(),
                      show_label = False))
        return v

if __name__ == '__main__':
    c = CanvasPreviewer()
    c.canvas.bootstrap('/Users/Ross/Desktop/canvas.elc')
    c.configure_traits()
#============= views ===================================
#============= EOF ====================================
