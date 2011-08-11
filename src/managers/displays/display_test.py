##============= enthought library imports =======================
#from traits.api import HasTraits, Instance
#from traitsui.api import View, Item, Group, HGroup, VGroup
#
##============= standard library imports ========================
#
##============= local library imports  ==========================
#from src.managers.displays.rich_text_display import RichTextDisplay, TextDisplay
#from pyface.timer.do_later import do_later
#from threading import Thread
#import time
#
#
#class Demo(HasTraits):
#    display = Instance(TextDisplay)
#    def _display_default(self):
#        return RichTextDisplay()
##    def _display_default(self):
##        return TextDisplay()
#    def start(self):
#        t = Thread(target = self._start)
#        t.start()
#
#    def _start(self):
#        for i in range(1000):
#            self.display.add_text('asdfsd %i' % i, color = (255, 0, 0))
#            time.sleep(0.05)
##============= views ===================================
#    def traits_view(self):
#        v = View(Item('display', show_label = False,
#                      style = 'custom'),
#                 resizable = True
#                 )
#        return v
#if __name__ == '__main__':
#    r = Demo()
#    do_later(r.start)
#    r.configure_traits()
##============= EOF ====================================
