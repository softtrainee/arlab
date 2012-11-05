##===============================================================================
## Copyright 2012 Jake Ross
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##   http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##===============================================================================
#
##============= enthought library imports =======================
#from traits.api import HasTraits, Str, List, Float, Int
#from traitsui.api import View, Item, TabularEditor, HGroup, spring
##============= standard library imports ========================
##============= local library imports  ==========================
#from traitsui.tabular_adapter import TabularAdapter
#import math
#from src.experiment.processing.database_manager import DatabaseManager
#import struct
#from src.helpers.logger_setup import logging_setup
#
#class HolderAdapter(TabularAdapter):
#    columns = [('Hole', 'hid'), ('X', 'x'), ('Y', 'y')]
#    x_format = Str('%0.2f')
#    y_format = Str('%0.2f')
#
#class Hole(HasTraits):
#    hid = Int
#    x = Float
#    y = Float
#
#class Holder(DatabaseManager):
#    holes = List
#    name = Str
#
#    def save(self):
#        blob = ''.join([struct.pack('>ff', h.x, h.y) for h in self.holes])
#        name = self.name
#        self.db.add_irradiation_holder(name, geometry=blob)
#        self.db.commit()
#
#    def new(self, n=20, r=10):
#        self.holes = [Hole(hid=i + 1,
#                           x=r * math.cos(math.radians(-a + 90)),
#                           y=r * math.sin(math.radians(-a + 90))) for i, a in enumerate(range(0, 360, 360 / n))]
#
#    def traits_view(self):
#        v = View(
#                 HGroup(Item('name', show_label=False), spring),
#                 Item('holes', show_label=False,
#                      editor=TabularEditor(adapter=HolderAdapter())
#                      ),
#                 handler=SaveableHandler,
#                 buttons=SaveableButtons,
#                 width=200,
#                 height=500,
#                 resizable=True
#                 )
#        return v
#
#if __name__ == '__main__':
#    logging_setup('holder')
#    h = Holder()
#    h.new()
#    h.configure_traits()
##============= EOF =============================================
