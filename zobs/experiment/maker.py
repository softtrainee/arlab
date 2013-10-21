# @PydevCodeAnalysisIgnore
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
from traits.api import HasTraits, Str, Button, Bool, on_trait_change, Any, \
    Instance, String, Property, cached_property, Float, List
from traitsui.api import View, Item, TableEditor, VGroup, HGroup, Spring, spring, \
EnumEditor, UItem
from src.experiment.script_editable import ScriptEditable
from src.experiment.utilities.identifier import convert_identifier, SPECIAL_NAMES, \
    SPECIAL_MAPPING, convert_special_name
from src.experiment.automated_run.automated_run import AutomatedRun
from src.paths import paths
from src.constants import NULL_STR, SCRIPT_KEYS
import os
from src.regex import ALIQUOT_REGEX
#============= standard library imports ========================
#============= local library imports  ==========================
# class AutomatedRunSpec(HasTraits):
#    labnumber = String(enter_set=True, auto_set=False)
#    _labnumber = Any
#
#    position = Str
#    endposition = Str
#    labnumbers = Property(depends_on='project')
#    projects = Property
#    project = Any
#
#    weight = Float
#    comment = Str
#
#    #===========================================================================
#    # extract
#    #===========================================================================
#    extract_value = Property(depends_on='_extract_value')
#    _extract_value = Float
#
#    extract_units = Str(NULL_STR)
#    extract_units_names = List(['---', 'watts', 'temp', 'percent'])
#    _default_extract_units = 'watts'
#    duration = Float
#    cleanup = Float
#
#    pattern = Str
#    patterns = Property
#    #===========================================================================
#    # display only
#    #===========================================================================
#    irrad_level = Str
#    sample = Str

class AutomatedRunMaker(ScriptEditable):
#    add = Button
#    auto_increment = Bool(True)
    db = Any
    schedule_block = Any

    template_automated_run = Instance(AutomatedRun)

    def _template_automated_run_default(self):
        t = AutomatedRun(db=self.db)
        return t

    def load_run(self, ar):
        for attr in ('labnumber',
                     'cleanup',
                     'duration',
                     'extract_value',
                     'extract_units',
                     ):
            setattr(self, attr, getattr(ar, attr))

    def _extract_device_changed(self):
        if self.mass_spectrometer:
            self._load_default_scripts(key=self.labnumber)



#    @on_trait_change('labnumber')
#    def _labnumber_changed(self):
#
#        arun = self.automated_run
        # check for id in labtable
#        self._ok_to_add = False
#        db = self.db
#
# #        arun.run_info.sample = ''
# #        arun.aliquot = 0
# #        arun.irrad_level = ''
#        self.irrad_level = ''
#        self.sample = ''
#        labnumber = self.labnumber
#        print self.labnumber
#        if labnumber:
#
#            # convert labnumber (a, bg, or 10034 etc)
#            clabnumber = convert_identifier(labnumber)
# #            if isinstance(convert_identifier(labnumber), int):
# #                self._ok_to_add = True
# # #                arun.sample = convert_labnumber(convert_identifier(labnumber))
# #                self._load_default_scripts()
# #                return
#
#            ln = db.get_labnumber(clabnumber)
#            if ln:
#                self._ok_to_add = True
#                # set sample and irrad info
#                try:
# #                    arun.run_info.sample = ln.sample.name
#                    self.sample = ln.sample.name
#                except AttributeError:
#                    pass
#
# #                arun.run_info.irrad_level = self._make_irrad_level(ln)
#                self.irrad_level = self._make_irrad_level(ln)
#                print 'asdf', self.automated_run.labnumber, labnumber
#                # set default scripts
#                self._load_default_scripts(key=labnumber)
#            else:
#                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))

    def _make_irrad_level(self, ln):
        il = ''
        ipos = ln.irradiation_position
        if not ipos is None:
            level = ipos.level
            irrad = level.irradiation
            il = '{}{}'.format(irrad.name, level.name)
        return il

    def new_runs(self):
        '''
            return:  List AutomatedRun
        '''
#    def _add_fired(self):
#         ars = self.automated_runs
#        ar = self.automated_run
        # labnumber is a property so its not cloned by clone_traits
#        ln = ar.labnumber
        if self.position:
            s = int(self.position)
            e = int(self.endposition)
            if e:
                if e < s:
                    self.warning_dialog('Endposition {} must greater than start position {}'.format(e, s))
                    return
                nruns = []
                for i in range(e - s + 1):
#                    ar.position = str(s + i)
                    position = str(s + i)
                    nruns.extend(self._add_run(position))

            else:
                nruns = self._add_run()
        else:
            nruns = self._add_run()

        return nruns

    def _add_run(self, position=0):
#        ars = self.automated_runs
#        nar = ar.clone_traits()
#        ln = ar.labnumber
        nar = AutomatedRun(position=str(position),
                           extract_value=self.extract_value,
                           extract_units=self.extract_units,
                           duration=self.duration,
                           cleanup=self.cleanup,
                           mass_spectrometer=self.mass_spectrometer,
                           extract_device=self.extract_device
                           )
        ln = self.labnumber  # ar.labnumber
        if ALIQUOT_REGEX.match(ln):
            ln, a = ln.split('-')
            nar.aliquot = int(a)
            nar.user_defined_aliquot = True

        nar.labnumber = ln

#        if ar.analysis_type.startswith('blank') or ar.analysis_type == 'background':
#            nar.extract_value = 0
#            nar.extract_units = ''

#        if self.schedule_block and self.schedule_block != NULL_STR:
# #            print self.schedule_block
#            block = self._block_factory(self.schedule_block)
#            nruns = block.render(ar, self._current_group_id)
# #            ars.extend(nruns)
#            self._current_group_id += 1
#        else:
        nruns = [nar]

#        else:
#            if self.selected:
#                ind = self.automated_runs.index(self.selected[-1])
#                ars.insert(ind + 1, nar)
#            else:
#                ars.append(nar)

#        kw = dict()
#        if self.auto_increment:
#            rid = self._auto_increment(ar.labnumber)
#            npos = self._auto_increment(ar.position)
#            if rid:
#                kw['labnumber'] = rid
#            if npos:
#                kw['position'] = npos
#        else:
#            self._ok_to_add = False
        for ar in nruns:
#            self._add_hook(ar, **kw)
            self._set_script_info(ar.script_info)
        return nruns


    def _set_script_info(self, info):
        for sn in SCRIPT_KEYS:
            v = getattr(self, '{}_script'.format(sn))
            setattr(info, '{}_script_name'.format(sn), v.name)
#
#    def _add_hook(self, ar, **kw):
#        self._set_script_info(ar.script_info)
# #        self.automated_run = ar.clone_traits()
#        # if analysis type is bg, b- or a overwrite a few defaults
# #        if not ar.analysis_type == 'unknown':
# #            kw['position'] = ''
# #            kw['extract_value'] = 0
#
#        if not 'labnumber' in kw:
#            keys = SPECIAL_MAPPING.values()
#            if not ar.labnumber in keys:
#                kw['special_labnumber'] = NULL_STR
#            else:
#                kw['special_labnumber'] = ar.special_labnumber
#
#            kw['labnumber'] = ar.labnumber
#            kw['_labnumber'] = ar._labnumber
#
# #        self.automated_run.trait_set(**kw)
# #        self.trait_set(**kw)
# #        self._bind_automated_run(self.automated_run)
#===============================================================================
# handlers
#===============================================================================
    def __labnumber_changed(self):
        if self._labnumber != NULL_STR:
            self.labnumber = self._labnumber

    def _project_changed(self):
        self._labnumber = NULL_STR
        self.labnumber = ''

    def _labnumber_changed(self):
        if self.labnumber != NULL_STR:
            if not self.labnumber in SPECIAL_MAPPING.values():
                self.special_labnumber = NULL_STR

        self._ok_to_add = False
        db = self.db

#        arun.run_info.sample = ''
#        arun.aliquot = 0
#        arun.irrad_level = ''
        self.irrad_level = ''
        self.sample = ''
        labnumber = self.labnumber
        if labnumber:

            # convert labnumber (a, bg, or 10034 etc)
            clabnumber = convert_identifier(labnumber)
#            if isinstance(convert_identifier(labnumber), int):
#                self._ok_to_add = True
# #                arun.sample = convert_labnumber(convert_identifier(labnumber))
#                self._load_default_scripts()
#                return

            ln = db.get_labnumber(clabnumber)
            if ln:
                self._ok_to_add = True
                # set sample and irrad info
                try:
#                    arun.run_info.sample = ln.sample.name
                    self.sample = ln.sample.name
                except AttributeError:
                    pass

#                arun.run_info.irrad_level = self._make_irrad_level(ln)
                self.irrad_level = self._make_irrad_level(ln)
#                print 'asdf', self.automated_run.labnumber, labnumber
#                print self.mass_spectrometer, 'asfdd'
                # set default scripts
                self._load_default_scripts(key=labnumber)
            else:
                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))

    def _special_labnumber_changed(self):
        if self.special_labnumber != NULL_STR:
            ln = convert_special_name(self.special_labnumber)
            if ln:
                self.labnumber = ln
                self._labnumber = NULL_STR

#===============================================================================
# property get/st
#===============================================================================
    def _validate_extract_value(self, d):
        return self._validate_float(d)

    def _validate_float(self, d):
        try:
            return float(d)
        except ValueError:
            pass

    def _get_extract_value(self):
        v = self._extract_value
        return v

    def _set_extract_value(self, t):
        if t is not None:
#            if self.heat_step:
#                self.heat_step.extract_value = t
#            else:
            self._extract_value = t
            if not t:
                self.extract_units = '---'
            elif self.extract_units == '---':
                self.extract_units = self._default_extract_units

        else:
            self.extract_units = '---'

    def _get_projects(self):
        prs = dict([(pi, pi.name) for pi in self.db.get_projects()])
        if prs:
            self.project = pi
        return prs

    def _get_labnumbers(self):
        lns = []
        if self.project:
            lns = [str(ln.labnumber)
                    for s in self.project.samples
                        for ln in s.labnumbers]
        return [NULL_STR] + sorted(lns)

    @cached_property
    def _get_patterns(self):
        p = paths.pattern_dir
        patterns = [NULL_STR]
        extension = '.lp'
        if os.path.isdir(p):
            ps = os.listdir(p)
            if extension is not None:
                patterns += [os.path.splitext(pi)[0] for pi in ps if pi.endswith(extension)]

        return patterns

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(UItem('template_automated_run', style='custom'))
        return v
#    def _get_position_group(self):
#        grp = VGroup(
# #                         Item('autocenter',
# #                              tooltip='Should the extract device try to autocenter on the sample'
# #                              ),
#                         HGroup(Item('position',
#                                     tooltip='Set the position for this analysis. Examples include 1, P1, L2, etc...'
#                                     ),
#                                Item('endposition', label='End')
#                                ),
# #                         Item('multiposition', label='Multi. position run'),
#                         show_border=True,
#                         label='Position'
#                     )
#        return grp
#
#    def _get_info_group(self):
#        readonly = lambda x, **kw: Item(x, style='readonly', **kw)
#        grp = VGroup(readonly('sample',
#                              tooltip='Sample info retreived from Database'
#                              ),
#                       readonly('irrad_level',
#                              tooltip='Irradiation info retreived from Database',
#                              label='Irradiation'),
#                       Item('weight',
#                            label='Weight (mg)',
#                            tooltip='(Optional) Enter the weight of the sample in mg. Will be saved in Database with analysis'
#                            ),
#                       Item('comment',
#                            tooltip='(Optional) Enter a comment for this sample. Will be saved in Database with analysis'
#                            )
#                     )
#        return grp
#
#    def _get_extract_group(self):
#        sspring = lambda width = 17:Spring(springy=False, width=width)
#
#        extract_grp = VGroup(
#                             HGroup(sspring(width=33),
#                                    Item('extract_value', label='Extract',
#                                         tooltip='Set the extract value in extract units'
#                                         ),
#                                    spring,
#                                    Item('extract_units', editor=EnumEditor(name='extract_units_names'),
#                                    show_label=False),
#                                    ),
#                             Item('duration', label='Duration (s)',
#                                  tooltip='Set the number of seconds to run the extraction device.'
#                                  ),
#                             Item('cleanup', label='Cleanup (s)',
#                                  tooltip='Set the number of seconds to getter the sample gas'
#                                  ),
#                             # Item('ramp_rate', label='Ramp Rate (C/s)'),
#                             Item('pattern', editor=EnumEditor(name='patterns')),
#                             label='Extract',
#                             show_border=True
#                             )
#        return extract_grp

#    def traits_view(self):
#        pos_grp = self._get_position_group()
#        script_grp = self._get_script_group()
#        info_grp = self._get_info_group()
#        extract_grp = self._get_extract_group()
#        v = View(
#                 Item('project', editor=EnumEditor(name='projects'),
#                           tooltip='Select a project to constrain the labnumbers'
#                           ),
# #                 Item('special_labnumber', editor=EnumEditor(values=SPECIAL_NAMES),
# #                   tooltip='Select a special Labnumber for special runs, e.g Blank, Air, etc...'
# #                    ),
#                 HGroup(Item('labnumber',
#                          tooltip='Enter a Labnumber'
#                          ),
#                      Item('_labnumber', show_label=False,
#                          editor=EnumEditor(name='labnumbers'),
#                          tooltip='Select a Labnumber from the selected Project'
#                          )),
#                 info_grp,
#                 extract_grp,
#                 pos_grp,
#                 script_grp,
# #                 HGroup(Item('auto_increment'),
# #                                     spring,
# #                                     Item('add', show_label=False,
# #                                          enabled_when='ok_to_add'),
# #                                     ),
#                 )
#        return v
#============= EOF =============================================
