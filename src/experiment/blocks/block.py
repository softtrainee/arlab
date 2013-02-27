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
from traits.api import Str
from traitsui.api import View, Item, InstanceEditor, HGroup, VGroup, \
    EnumEditor, spring
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.blocks.base_schedule import BaseSchedule, RunAdapter
from src.experiment.automated_run import AutomatedRun
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.identifier import ANALYSIS_MAPPING

import os
from pyface.file_dialog import FileDialog
from pyface.constant import OK
from src.paths import paths
from src.constants import SCRIPT_KEYS, NULL_STR
from src.saveable import SaveableButtons

def line_generator(path, delim='\t'):
    with open(path, 'r') as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            yield line.split(delim)


class Block(BaseSchedule):

    analysis_type = Str#('bg')#Enum(ANALYSIS_MAPPING)
    _path = None
    def __init__(self, *args, **kw):
        super(Block, self).__init__(*args, **kw)
        self.analysis_type = 'bg'
#        self._load_default_scripts(key=self.analysis_type)

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

            params, _ = cls.parse_line(header, line, meta)
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

            params, _ = self.parse_line(header, line, meta)
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
#    def update_loaded_scripts(self, new):
#        if new:
#            self.loaded_scripts[new.name] = new

    def _analysis_type_changed(self):
        if self.analysis_type != NULL_STR:
            self._load_default_scripts(key=self.analysis_type)

            ar = self.automated_run
            ar.configuration = self.make_configuration()

#            ar.extraction_script_dirty = True
#            ar.measurement_script_dirty = True
#            ar.post_measurement_script_dirty = True
#            ar.post_equilibration_script_dirty = True
#            ar.create_scripts()


    def _add_fired(self):
#        ar = self.automated_run
        ars = self.automated_runs

#        print self.automated_run.scripts
#        self._bind_automated_run(self.automated_run, remove=True)

        ar = self.automated_run.clone_traits()
#        print ar.scripts, self.loaded_scripts
#        ar.configuration = self.make_configuration()

#        ar.extraction_script_dirty = True
#        ar.measurement_script_dirty = True
#        ar.post_measurement_script_dirty = True
#        ar.post_equilibration_script_dirty = True
#        ar.create_scripts()

#        print ar.extraction_script
        if ar.executable:
            ars.append(ar)

#        self._bind_automated_run(self.automated_run)
#            self.automated_run = ar.clone_traits()
#            self._add_hook(ar)


#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        new_analysis = VGroup(
                              Item('automated_run',
                                   show_label=False,
                                   style='custom',
                                   editor=InstanceEditor(view='simple_view')
                                   ),
                              enabled_when='mass_spectrometer and mass_spectrometer!="---"'
                              )

        analysis_table = VGroup(
                                self._get_copy_paste_group(),
                                Item('runs_table', show_label=False, style='custom'),
                                show_border=True,
                                label='Analyses',
                                )
        script_grp = self._get_script_group()
#        vs = {'---':NULL_STR}
#        vs.update(ANALYSIS_MAPPING)
        lgrp = VGroup(

                      Item('analysis_type',
#                           editor=EnumEditor(values=vs),
                           editor=EnumEditor(values=ANALYSIS_MAPPING),
                           show_label=False),
                      new_analysis,
#                      Item('automated_run', style='custom',
#                           show_label=False,
#                           editor=InstanceEditor(view='simple_view')),
                      script_grp,
                      HGroup(spring, Item('add', show_label=False))
                      )

        v = View(HGroup(lgrp, analysis_table),
                 handler=self.handler_klass,
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
