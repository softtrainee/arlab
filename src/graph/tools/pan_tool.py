#============= enthought library imports =======================
from chaco.tools.api import PanTool
#============= standard library imports ========================

#============= local library imports  ==========================
class MyPanTool(PanTool):
    '''
        G{classtree}
    '''
    active = False
    def normal_key_pressed(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        #print self.component
        if event.character == 'p':
            self.active = not self.active

        elif event.character == 'Esc':
            c = self.component
            for r in ['index', 'value']:
                ra = getattr(c, '%s_range' % r)
                for s in ['low', 'high']:
                    ra.trait_set(**{'%s_setting' % s:'auto'})

        event.handled = True

    def normal_left_down(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        if self.active:
            PanTool.normal_left_down(self, event)
#============= EOF ====================================
