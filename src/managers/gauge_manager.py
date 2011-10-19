'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
from traits.api import HasTraits, List
from traitsui.api import View, Item
from src.managers.manager import Manager
#============= standard library imports ========================
#============= local library imports  ==========================

class GaugeManager(Manager):
#    def finish_loading(self, *args, **kw):
#        print 'load gm', args, kw
#        
#        for k, v in self.traits().items():
#            if 'gauge_controller' in k:
#                print v
#                
    def start_scans(self):
        for k in self.devices:
            k.start_scan()
#            if 'gauge_controller' in k:
#                print v
#                v.start_scan()
#                
        
            
    def traits_view(self):
        v = View()
        return v
#    controllers = List(GaugeControllers)
if __name__ == '__main__':
    g = GaugeManager()
    g.configure_traits()
#============= EOF =====================================
