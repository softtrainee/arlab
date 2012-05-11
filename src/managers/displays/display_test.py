#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



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
