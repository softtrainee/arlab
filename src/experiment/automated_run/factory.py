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
from traits.api import HasTraits, String, Str, Property, Any, Either, Long, \
     Float, Instance, Int, List, cached_property, on_trait_change, Bool
from traitsui.api import View, Item, EnumEditor, HGroup, VGroup, Group, Spring, spring
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.loggable import Loggable
from src.constants import NULL_STR, SCRIPT_KEYS, SCRIPT_NAMES
from src.experiment.utilities.identifier import SPECIAL_NAMES, SPECIAL_MAPPING, \
    convert_identifier, convert_special_name
from src.experiment.automated_run.spec import AutomatedRunSpec
from src.regex import TRANSECT_REGEX, POSITION_REGEX
from src.experiment.utilities.script_mixin import ScriptMixin
from src.paths import paths
from src.experiment.script.script import Script


class AutomatedRunFactory(Loggable, ScriptMixin):
    db = Any

    labnumber = String(enter_set=True, auto_set=False)
    aliquot = Long
    o_aliquot = Either(Long, Int)
    user_defined_aliquot = False
    special_labnumber = Str

    _labnumber = Str
    labnumbers = Property(depends_on='project')

    project = Any
    projects = Property

    skip = Bool(False)
    weight = Float
    comment = Str

    position = Property(depends_on='_position')
    _position = Str
    endposition = Int
    #===========================================================================
    # extract
    #===========================================================================
    extract_value = Property(depends_on='_extract_value')
    _extract_value = Float
    extract_units = Str(NULL_STR)
    extract_units_names = List(['---', 'watts', 'temp', 'percent'])
    _default_extract_units = 'watts'

    duration = Float
    cleanup = Float

    pattern = Str
    patterns = Property

    #===========================================================================
    # readonly
    #===========================================================================
    sample = Str
    irradiation = Str
    #===========================================================================
    # private
    #===========================================================================
    _selected_runs = None
    _spec_klass = AutomatedRunSpec


    def load_from_run(self, run):
        self._clone_run(run)

    def commit_changes(self, runs):
        for i, ri in enumerate(runs):
            self._set_run_values(ri, excludes='labnumber')

            if self.aliquot:
                ri.aliquot = self.aliquot + i
                ri.user_defined_aliquot = True
            else:
                ri.user_defined_aliquot = False

    def set_selected_runs(self, runs):
        self._selected_runs = runs
        if runs:
            run = runs[0]
            self._clone_run(run)

    def new_runs(self, auto_increment=False):
        '''
            returns a list of runs even if its only one run
        '''
        s = 0
        e = 0
        if self.position:
            s = int(self.position)
            e = int(self.endposition)
            if e:
                if e < s:
                    self.warning_dialog('Endposition {} must greater than start position {}'.format(e, s))
                    return
                arvs = []
                for i in range(e - s + 1):
#                    ar.position = str(s + i)
                    position = str(s + i)
                    arvs.append(self._new_run(position=position))
                    '''
                        clear user_defined_aliquot flag
                        if adding multiple runs this allows 
                        the subsequent runs to have there aliquots defined by db
                    '''
                    self.user_defined_aliquot = False

            else:
                arvs = [self._new_run(position=str(s))]
        else:
            arvs = [self._new_run()]

        if auto_increment:

            if self.position:
                self.position = str(e + 1)
            if self.endposition:
                self.endposition = 2 * e + 1 - s
            self.labnumber = self._increment(self.labnumber)

        return arvs

    def set_mass_spectrometer(self, new):
        new = new.lower()
        self.mass_spectrometer = new
        for s in SCRIPT_NAMES:
            sc = getattr(self, s)
            sc.mass_spectrometer = new

    def set_extract_device(self, new):
        new = new.lower()
        self.extract_device = new
        for s in SCRIPT_KEYS:
            s = getattr(self, '{}_script'.format(s))
            s.extract_device = new

#===============================================================================
# private
#===============================================================================
    def _increment(self, m):
        try:
            m = str(int(m) + 1)
        except ValueError:
            pass

        return m

    def _make_irrad_level(self, ln):
        il = ''
        ipos = ln.irradiation_position
        if not ipos is None:
            level = ipos.level
            irrad = level.irradiation
            il = '{}{}'.format(irrad.name, level.name)
        return il

    def _new_run(self, **kw):
        arv = self._spec_klass(**kw)
        self._set_run_values(arv)
        return arv

    def _set_run_values(self, arv, excludes=None):
        if excludes is None:
            excludes = []

        for attr in ('labnumber',
                     'extract_value', 'extract_units', 'cleanup', 'duration',
                     'weight', 'comment',
                     'sample', 'irradiation',
                     'skip', 'mass_spectrometer'
                     ):

            if attr in excludes:
                continue

            setattr(arv, attr, getattr(self, attr))

        if self.user_defined_aliquot:
            arv.user_defined_aliquot = True
            arv.aliquot = int(self.aliquot)

        for si in SCRIPT_KEYS:
            name = '{}_script'.format(si)
            if name in excludes or si in excludes:
                continue

            s = getattr(self, name)
#            print s.name
            setattr(arv, name, s.name)


    def _clone_run(self, run, excludes=None):
        if excludes is None:
            excludes = []
        for attr in ('labnumber',
                     'extract_value', 'extract_units', 'cleanup', 'duration',
                     'weight', 'comment'):
            if attr in excludes:
                continue
            setattr(self, attr, getattr(run, attr))

        if run.user_defined_aliquot:
            self.aliquot = run.aliquot

        for si in SCRIPT_KEYS:
            name = '{}_script'.format(si)
            s = getattr(run, name)
            if name in excludes or si in excludes:
                continue

            setattr(self, name, Script(name=s,
                                       label=si,
                                       application=self.application,
                                       mass_spectrometer=self.mass_spectrometer))

#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('cleanup, duration, extract_value, extract_units, position')
    def _edit_handler(self, name, new):
        if self._selected_runs:
            for si in self._selected_runs:
                setattr(si, name, new)

    @on_trait_change('''measurement_script:name, 
extraction_script:name, 
post_measurement_script:name,
post_equilibration_script:name
    ''')
    def _edit_script_handler(self, obj, name, new):
        if self._selected_runs:
            for si in self._selected_runs:
                name = '{}_script'.format(obj.label)
                setattr(si, name, new)

    def __labnumber_changed(self):
        if self._labnumber != NULL_STR:
            self.labnumber = self._labnumber

    def _project_changed(self):
        self._labnumber = NULL_STR
        self.labnumber = ''

    def _special_labnumber_changed(self):
        if self.special_labnumber != NULL_STR:
            ln = convert_special_name(self.special_labnumber)
            if ln:
                self.labnumber = ln
                self._labnumber = NULL_STR

    def _aliquot_changed(self):
        if self.aliquot != self.o_aliquot:
            self.user_defined_aliquot = True
        else:
            self.user_defined_aliquot = False

    def _labnumber_changed(self):
        if self.labnumber != NULL_STR:
            if not self.labnumber in SPECIAL_MAPPING.values():
                self.special_labnumber = NULL_STR
        self.irradiation = ''
        self.sample = ''

        db = self.db
        if not db:
            return
#        arun.run_info.sample = ''
#        arun.aliquot = 0
#        arun.irradiation = ''
        labnumber = self.labnumber
        if labnumber:

            # convert labnumber (a, bg, or 10034 etc)
            clabnumber = convert_identifier(labnumber)
            ln = db.get_labnumber(clabnumber)
            if ln:
                # set sample and irrad info
                try:
                    self.sample = ln.sample.name
                except AttributeError:
                    pass

                try:
                    a = ln.analyses[-1].aliquot + 1
                    self.o_aliquot = a
                except IndexError, e:
                    self.debug('Lanbumer changed IndexError:{}'.format(e))
                    a = 1
                self.aliquot = a
#                self.trait_set(aliquot=a, trait_change_notify=False)

                self.irradiation = self._make_irrad_level(ln)
                # set default scripts
                self._load_default_scripts(key=labnumber)
            else:
                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))
#===============================================================================
# property get/set
#===============================================================================
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

    def _get_position(self):
        return self._position

    def _set_position(self, pos):
        self._position = pos

    def _validate_position(self, pos):
        if not pos.strip():
            return ''

        ps = pos.split(',')
#        try:
        ok = False
        for pi in ps:
            if not pi:
                continue

            ok = False
            if TRANSECT_REGEX.match(pi):
                ok = True

            elif POSITION_REGEX.match(pi):
                ok = True

        if not ok:
            pos = self._position
        return pos

    def _validate_extract_value(self, d):
        return self._validate_float(d)

    def _validate_float(self, d):
        try:
            return float(d)
        except ValueError:
            pass

    def _get_extract_value(self):
        return self._extract_value

    def _set_extract_value(self, t):
        if t is not None:
            self._extract_value = t
            if not t:
                self.extract_units = NULL_STR
            elif self.extract_units == NULL_STR:
                self.extract_units = self._default_extract_units
        else:
            self.extract_units = NULL_STR

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
# groups
#===============================================================================
    def _get_info_group(self):
        grp = Group(
                   Item('project', editor=EnumEditor(name='projects'),
                       tooltip='Select a project to constrain the labnumbers'
                       ),
                   Item('special_labnumber', editor=EnumEditor(values=SPECIAL_NAMES),
                       tooltip='Select a special Labnumber for special runs, e.g Blank, Air, etc...'
                       ),
                   HGroup(Item('labnumber',
                              tooltip='Enter a Labnumber'
                              ),
                          Item('_labnumber', show_label=False,
                              editor=EnumEditor(name='labnumbers'),
                              tooltip='Select a Labnumber from the selected Project'
                              ),
                         ),
                   Item('aliquot'),
                   Item('sample',
                        tooltip='Sample info retreived from Database',
                        style='readonly'
                        ),
                   Item('irradiation',
                          tooltip='Irradiation info retreived from Database',
                          style='readonly'
                          ),
                   Item('weight',
                        label='Weight (mg)',
                        tooltip='(Optional) Enter the weight of the sample in mg. Will be saved in Database with analysis'
                        ),
                   Item('comment',
                        tooltip='(Optional) Enter a comment for this sample. Will be saved in Database with analysis'
                        ),
#                       extract_grp,
                       show_border=True,
                       label='Info'
                       )
        return grp

    def _get_script_group(self):
        script_grp = VGroup(
                        Item('extraction_script', style='custom', show_label=False),
                        Item('measurement_script', style='custom', show_label=False),
                        Item('post_equilibration_script', style='custom', show_label=False),
                        Item('post_measurement_script', style='custom', show_label=False),
                        show_border=True,
                        label='Scripts'
                        )
        return script_grp

    def _get_position_group(self):
        grp = VGroup(
 #                         Item('autocenter',
 #                              tooltip='Should the extract device try to autocenter on the sample'
 #                              ),
                         HGroup(Item('position',
                                     tooltip='Set the position for this analysis. Examples include 1, P1, L2, etc...'
                                     ),
                                Item('endposition', label='End',
                                     enabled_when='position'
                                     )
                                ),
 #                         Item('multiposition', label='Multi. position run'),
                         show_border=True,
                         label='Position'
                     )
        return grp

    def _get_extract_group(self):
        sspring = lambda width = 17:Spring(springy=False, width=width)

        extract_grp = VGroup(
                             HGroup(sspring(width=33),
                                    Item('extract_value', label='Extract',
                                         tooltip='Set the extract value in extract units'
                                         ),
                                    spring,
                                    Item('extract_units', editor=EnumEditor(name='extract_units_names'),
                                    show_label=False),
                                    ),
                             Item('duration', label='Duration (s)',
                                  tooltip='Set the number of seconds to run the extraction device.'
                                  ),
                             Item('cleanup', label='Cleanup (s)',
                                  tooltip='Set the number of seconds to getter the sample gas'
                                  ),
                             # Item('ramp_rate', label='Ramp Rate (C/s)'),
                             Item('pattern', editor=EnumEditor(name='patterns')),
                             label='Extract',
                             show_border=True
                             )
        return extract_grp
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        info_grp = self._get_info_group()
        script_grp = self._get_script_group()
        extract_grp = self._get_extract_group()
        pos_grp = self._get_position_group()
        v = View(
                 VGroup(info_grp,
                        extract_grp,
                        pos_grp,
                        script_grp,
                        )
                 )
        return v

    def edit_view(self):
        extract_group = self._get_extract_group()
        v = View(
                 Item('skip',
                      tooltip='exclude this run from execution'
                      ),
                 Item('labnumber', style='readonly'),
                 Item('aliquot'),
                 extract_group,
                 title='Edit Automated Runs',
                 buttons=['OK', 'Cancel'],
                 resizable=True
                 )
        return v



#============= EOF =============================================
