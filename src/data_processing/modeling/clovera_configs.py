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
from traits.api import  Str, Int, Float, Bool
from traitsui.api import View, Item, ModalButtons, Handler
#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.loggable import Loggable
class BaseConfigHandler(Handler):
    def closed(self, info, is_ok):
        if is_ok:
            info.object.dump()
            
class BaseConfig(Loggable):
    root = None
    runid = Str
    _dump_attrs = None
    def __init__(self, rid, root, *args, **kw):
        super(BaseConfig, self).__init__(*args, **kw)
        self.runid = rid
        self.root = root
        
    def dump(self):
        if not self._dump_attrs:
            raise NotImplementedError('set _dump_attrs')
        
        p = self.get_path()
        self.info('saving configuration to {}'.format(p))
        with open(p, 'w') as f:
            txt = '\n'.join([str(getattr(self, attr)) for attr in self._dump_attrs])
            f.write(txt)
            
    def get_path(self):
        p = os.path.join(self.root, self.runid, '{}.cl'.format(self.klass_name))
        return p
    
    def _get_buttons(self):
        return ModalButtons[1:]
    
class AutoUpdateParseConfig(BaseConfig):
    tempoffset = Float
    timeoffset = Float

    def traits_view(self):
        v = View('tempoffset',
               'timeoffset',
               buttons=self._get_buttons(),
               kind='livemodal'
               )
        return v   
    
class FilesConfig(BaseConfig):
    klass_name = 'files'
    #===========================================================================
    # config params
    #===========================================================================
    
    STOP = 'stop'
    _dump_attrs = ['runid', 'STOP']
            
class AutoarrConfig(BaseConfig):
    klass_name = 'autoarr'
    #===========================================================================
    # config params
    #===========================================================================
    calc_arrhenius_parameters = Bool(False)
    max_domains = Int
    min_domains = Int
    fixed_Do = Bool
    activation_energy = Float
    ordinate_Do = Float
    
    _dump_attrs = ['calc_arrhenius_parameters',
               'max_domains',
               'min_domains',
               'fixed_Do',
               'ordinate_Do'
               ]
    
    def traits_view(self):
        v = View(Item('calc_arrhenius_parameters'),
               Item('max_domains'),
               Item('min_domains'),
               Item('fixed_Do'),
               Item('ordinate_Do'),
               buttons=self._get_buttons(),
               handler=BaseConfigHandler,
               title='Autoarr Configuration',
               kind='livemodal'
               
               )
        
        return v
    
class AutoagemonConfig(BaseConfig):
    klass_name = 'autoagemon'
    #===========================================================================
    # config params
    #===========================================================================
    nruns = Int(50)
    max_plateau_age = Float(1000)
    _dump_attrs = ['nruns', 'max_plateau_age']
    def traits_view(self):
        v = View(Item('nruns'),
                 Item('max_plateau_age', label='Max. Plateua Age (Ma)'),
                 buttons=self._get_buttons(),
                 handler=BaseConfigHandler,
                 title='Autoagemon Configuration',
                 kind='livemodal'
               )
        return v
    
class AutoagefreeConfig(BaseConfig):
    klass_name = 'autoagefree'
    #===========================================================================
    # config params
    #===========================================================================
    nruns = Int(50)
    max_plateau_age = Float(1000)
    _dump_attrs = ['nruns', 'max_plateau_age']
    def traits_view(self):
        v = View(Item('nruns'),
                 Item('max_plateau_age', label='Max. Plateua Age (Ma)'),
                 buttons=self._get_buttons(),
                 handler=BaseConfigHandler,
                 title='Autoagefree Configuration',
                 kind='livemodal'
               )
        return v
    
class ConfidenceIntervalConfig(BaseConfig):
    klass_name = 'confint'
    #===========================================================================
    # config params
    #===========================================================================
    max_age = Float(500)
    min_age = Float(0)
    nsteps = Int(100)
    
    _dump_attrs = ['max_age', 'min_age', 'nsteps']
    def traits_view(self):
        v = View(Item('max_age'),
                 Item('min_age'),
                 Item('nsteps'),
                 buttons=self._get_buttons(),
                 handler=BaseConfigHandler,
                 title='Confidence Interval Configuration',
                 kind='livemodal'
               )
        return v
    
    
if __name__ == '__main__':
    a = ConfidenceIntervalConfig('12345-01', '/Users/Ross/Desktop')
    info = a.configure_traits()
    if info:
        print 'foo'
        
#============= EOF =====================================

