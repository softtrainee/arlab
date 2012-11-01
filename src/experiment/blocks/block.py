#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Str, Any
from traitsui.api import View, Item, InstanceEditor, HGroup, VGroup, \
    EnumEditor, spring
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.blocks.base_schedule import BaseSchedule, RunAdapter
from src.experiment.automated_run import AutomatedRun
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.identifier import ANALYSIS_MAPPING
from src.managers.manager import SaveableHandler, SaveableButtons
import os
from pyface.file_dialog import FileDialog
from pyface.constant import OK
from src.paths import paths
from constants import SCRIPT_KEYS, NULL_STR

def line_generator(path, delim='\t'):
    with open(path, 'r') as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            yield line.split(delim)


class Block(BaseSchedule):

    analysis_type = Str('bg')#Enum(ANALYSIS_MAPPING)
    _path = None
    def __init__(self, *args, **kw):
        super(Block, self).__init__(*args, **kw)
        self._load_default_scripts(key=self.analysis_type)

    @property
    def name(self):
        if self._path:
            return os.path.basename(self._path)

    @classmethod
    def is_template(cls, path):
        path = os.path.join(paths.block_dir, path)
        line_gen = line_generator(path)
        header = None
        for line in line_gen:
            if header is None:
                header = line
                continue

            meta = None
            params = cls._run_parser(header, line, meta)
            try:
                ln = params['labnumber']
                if ln.lower() == 'u':
                    return True
            except KeyError:
                pass

#===============================================================================
# persistence
#===============================================================================
    def save(self):
        if os.path.isfile(self._path):
            self._save(self._path)

    def save_as(self):
        dlg = FileDialog(action='save as',
                         default_directory=paths.block_dir)

        if dlg.open() == OK:
            self._save(dlg.path)

#        self._save(os.path.join(paths.block_dir, 'foo'))

    def _save(self, path):
        if path:
            self.info('saving block {} to {}'.format(self.name, path))
            self._path = path
            with open(path, 'w') as fp:
                self.dump(fp)

    def load(self, path):
        '''
            load from file
        '''
#        delim = '\t'
        header = None
        line_gen = line_generator(path)
#        with open(path, 'r') as fp:
        meta = dict(mass_spectrometer=self.mass_spectrometer,
                    extract_device=self.extract_device
                    )

        for line in line_gen:
            if header is None:
                header = line
                continue

            params = self._run_parser(header, line, meta)
            params['mass_spectrometer'] = self.mass_spectrometer
            params['extract_device'] = self.extract_device
            params['scripts'] = self.loaded_scripts
            a = AutomatedRun(**params)
            if a.labnumber.lower() == 'u':
                self.is_template = True

            self._bind_automated_run(a)
            a.create_scripts()
            self.automated_runs.append(a)

        return True

#===============================================================================
# render
#===============================================================================
    def render(self, run, extract_group_id):
        return [self._render(ai, run, extract_group_id) for ai in self.automated_runs]

    def _render(self, template_run, input_run, extract_group_id):
        if template_run.labnumber.lower() == 'u':
            template_run.copy_traits(input_run, traits=['labnumber', ])
            template_run.extract_group = extract_group_id
        return template_run

#===============================================================================
# handlers
#===============================================================================

    def _analysis_type_changed(self):
        self._load_default_scripts(key=self.analysis_type)

    def _add_fired(self):
        arun = self.automated_run
        arun.trait_set(labnumber=self.analysis_type,
                       mass_spectrometer=self.mass_spectrometer,
                       extraction_device=self.extract_device,
                        scripts=self.loaded_scripts)
        self._bind_automated_run(arun)

        arun.configuration = dict()
        for ki in SCRIPT_KEYS:
            sname = '{}_script'.format(ki)
            si = getattr(self, sname)
            if si:
                si = self._add_mass_spectromter_name(si)
                arun.configuration[sname] = os.path.join(paths.scripts_dir,
                                                      ki, si)
            else:
                arun.configuration[sname] = NULL_STR
                setattr(arun, '{}_script_dirty'.format(ki), True)
#            setattr(arun, '{}_script'.format(ki),)
#        arun = self.automated_run.clone_traits()
        self.automated_runs.append(arun.clone_traits())
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        r = myTabularEditor(adapter=RunAdapter(),
#                             update=update,
#                             right_clicked='object.right_clicked',
                             selected='object.selected',
#                             refresh='object.refresh',
#                             activated_row='object.activated_row',
                             operations=['delete', 'edit'],
                             editable=True,
                             auto_resize=True,
                             multi_select=True,
                             auto_update=True,
                             scroll_to_bottom=False
                            )

        script_grp = self._get_script_group()
        lgrp = VGroup(

                      Item('analysis_type',
                           editor=EnumEditor(values=ANALYSIS_MAPPING),
                           show_label=False),
                      Item('automated_run', style='custom',
                           show_label=False,
                           editor=InstanceEditor(view='simple_view')),
                      script_grp,
                      HGroup(spring, Item('add', show_label=False))
                      )
        rgrp = VGroup(
                      self._get_copy_paste_group(),
                      Item('automated_runs', show_label=False, editor=r))
        v = View(HGroup(lgrp, rgrp),
                 handler=SaveableHandler,
                 buttons=SaveableButtons,
                 resizable=True,
                 width=1000,
                 height=500
                 )
        return v
if __name__ == '__main__':
    from launchers.helpers import build_version
    build_version('_experiment')
    from src.helpers.logger_setup import logging_setup
    logging_setup('block')

    s = Block(mass_spectrometer='obama', extract_devic='Fusions CO2')
    s.load(os.path.join(paths.block_dir, 'foo'))
#    s.automated_runs = [AutomatedRun(check_executable=False) for _ in range(4)]
    s.configure_traits()
#============= EOF =============================================
