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



#============= enthought library imports =======================
from traits.api import HasTraits, Any, Instance, List, \
    on_trait_change, DelegatesTo, Str, Property
from traitsui.api import View, Item, EnumEditor
from pyface.timer.api import Timer
#============= standard library imports ========================
import os
#============= local library imports  ==========================

#============= views ===================================
from envisage_script import EnvisageScript
from script_validator import ScriptValidator
from src.envisage.core.envisage_manager import EnvisageManager
from src.envisage.core.envisage_editor import EnvisageEditor
from src.helpers.paths import scripts_dir
RUNSCRIPT_DIR = os.path.join(scripts_dir, 'runscripts')

class SEditor(EnvisageEditor):
    name = 'Script'
#    def _name_default(self):
#        '''
#        '''
#        return self.obj.name
#
#    def create_control(self, parent):
#        '''
#            @type parent: C{str}
#            @param parent:
#        '''
#        script = self.obj
#        ui = script.edit_traits(parent = parent, kind = 'subpanel'
#                                )
#        return ui.control

class ScriptSelector(HasTraits):
    names = ['BakeoutScript', 'ExtractionLineScript', 'PowerScanScript', 'PowerMapScript']
    scripts = dict(
                   BakeoutScript=['bakeout_script', None],
                   ExtractionLineScript=['extraction_line_script',
                                            'src.managers.extraction_line_manager.ExtractionLineManager'],
                   PowerScanScript=['laser.power_scan_script',
                                      ('src.managers.laser_managers.fusions_diode_manager.FusionsDiodeManager',
                                       'src.managers.laser_managers.fusions_co2_manager.FusionsCO2Manager',
                                       )],
                   PowerMapScript=['laser.power_map_script',
                                      ('src.managers.laser_managers.fusions_diode_manager.FusionsDiodeManager',
                                       'src.managers.laser_managers.fusions_co2_manager.FusionsCO2Manager',
                                       )],
                   )
    selected = Property(depends_on='_selected')
    _selected = Str('BakeoutScript')

    v = View(Item('selected', show_label=False, editor=EnumEditor(values=names)),
             kind='modal',
             buttons=['OK', 'Cancel']
             )

    def _get_selected(self):
        return self._selected, 'src.scripts.%s' % self.scripts[self._selected][0], self.scripts[self._selected][1]

    def _set_selected(self, s):
        self._selected = s


class ScriptsManager(EnvisageManager):
    '''
        G{classtree}
    '''

    scripts = List(EnvisageScript)
    klass = EnvisageScript

    script_package = 'src.scripts.laser.power_map_script'
    script_klass = 'PowerMapScript'

    manager_protocol = ('src.managers.laser_managers.fusions_diode_manager.FusionsDiodeManager',
                        'src.managers.laser_managers.fusions_co2_manager.FusionsCO2Manager',
                        )

    editor_klass = SEditor

    validator = Instance(ScriptValidator)
    errors = DelegatesTo('validator')
    wildcard = '*.rs'
    default_directory = RUNSCRIPT_DIR

    process_view = Any
    def run(self):
        self.selected.execute()

    @on_trait_change('window:editor_opened')
    def start_validation(self, object, name, old, new):
        '''
            @type object: C{str}
            @param object:

            @type name: C{str}
            @param name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        if isinstance(new, SEditor):
            self.vtimer = Timer(500, self._do_validation)
            print 'ad'
            object.active_editor = new

    @on_trait_change('window:editor_closing')
    def _on_editor_closed(self, obj, trait_name, old, new):
        '''
            @type obj: C{str}
            @param obj:

            @type trait_name: C{str}
            @param trait_name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        if isinstance(new, SEditor):
            self.scripts.remove(new.obj)

    def _do_validation(self):
        '''
        '''
        if self.scripts:
            self.validator.errors = []
            for script in self.scripts:

                self.validator.validate(script, file=script.name)
        else:
            self.validator.errors = []

    def _validator_default(self):
        '''
        '''
        return ScriptValidator(parent=self)

    def add_and_edit(self, s, new=False):

        if new:
            self.process_view.dirty = True
        else:
            self.process_view.dirty = False

        self.scripts.append(s)
        self.selected = s
        s.parent = self
        self.window.workbench.edit(s,
                                   kind=self.editor_klass,
                                   use_existing=False)

    def new(self):
        '''
        '''
        #get the script kind

        ss = ScriptSelector()
        info = ss.edit_traits()
        if info.result:

            sk, sp, ma = ss.selected

            kw = dict(script_package=sp,
                      script_klass=sk,
                      _name=sk
                      )

            if ma is not None:
                kw['manager'] = self.get_service(ma)

            s = self.klass_factory(**kw)
            s.bootstrap()
            self.add_and_edit(s, new=True)


    def klass_factory(self, **kw):

        if not kw:

            kw = dict(script_package=self.script_package,
                    script_klass=self.script_klass,
                    manager=self.get_service(self.manager_protocol)
                    )

        s = self.klass(
                   **kw
                   )

        return s

    def open_default(self):
        '''
        '''
#        p = '/Users/Ross/Pychrondata_beta/scripts/runscripts/1valid.rs'
#        if os.path.isfile(p):
#            self.open(path = p)
#        else:
#            self.new()     
        pass
    def error_view(self):
        '''
        '''
        return View(Item('validator', show_label=False, style='custom'))
#============= EOF ====================================
