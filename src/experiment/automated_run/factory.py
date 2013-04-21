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
     Float, Instance, Int, List, cached_property, on_trait_change, Bool, Button, \
     Event
from traitsui.api import View, Item, EnumEditor, HGroup, VGroup, Group, Spring, spring, \
    UItem, ButtonEditor, Label
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.constants import NULL_STR, SCRIPT_KEYS, SCRIPT_NAMES
from src.experiment.utilities.identifier import SPECIAL_NAMES, SPECIAL_MAPPING, \
    convert_identifier, convert_special_name, ANALYSIS_MAPPING, NON_EXTRACTABLE, \
    make_special_identifier, make_standard_identifier
from src.experiment.automated_run.spec import AutomatedRunSpec
from src.regex import TRANSECT_REGEX, POSITION_REGEX
from src.experiment.utilities.script_mixin import ScriptMixin
from src.paths import paths
from src.experiment.script.script import Script
from src.experiment.queue.increment_heat_template import IncrementalHeatTemplate
from src.viewable import Viewable

def CBItem(name, **kw):
    return HGroup(Item(name, **kw), UItem('cb_{}'.format(name),
                                          visible_when='cbs_enabled'
                                          ))

class AutomatedRunFactory(Viewable, ScriptMixin):
    db = Any

    labnumber = String(enter_set=True, auto_set=False)
    aliquot = Long
    o_aliquot = Either(Long, Int)
    user_defined_aliquot = False
    special_labnumber = Str

    _labnumber = Str
    labnumbers = Property(depends_on='project, selected_level')

    project = Any
    projects = Property(depends_on='db')

    selected_irradiation = Any
    irradiations = Property(depends_on='db')
    selected_level = Any
    levels = Property(depends_on='selected_irradiation, db')

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
    # checkboxes
    #===========================================================================
    cb_pattern = Bool
    cb_cleanup = Bool
    cb_duration = Bool
    cb_position = Bool
    cb_extract_value = Bool
    cb_extract_units = Bool

    cb_comment = Bool
    cb_weight = Bool

    #===========================================================================
    # templates
    #===========================================================================
    template = String
    templates = Property
#    edit_template = Button('edit')
    edit_template = Event
    edit_template_label = Property(depends_on='template')
    #===========================================================================
    # frequency
    #===========================================================================
    frequency = Int

    #===========================================================================
    # readonly
    #===========================================================================
    sample = Str
    irradiation = Str

    #===========================================================================
    # private
    #===========================================================================
    _selected_runs = List
    _spec_klass = AutomatedRunSpec
    _extract_group_cnt = 1

#    frequencyable = Property(depends_on='labnumber')
    extractable = Property(depends_on='labnumber')
    cbs_enabled = Property(depends_on='_selected_runs')

    def use_frequency(self):
        return self.labnumber in ANALYSIS_MAPPING and self.frequency

    def load_from_run(self, run):
        self._clone_run(run)

    def commit_changes(self, runs):
        for i, ri in enumerate(runs):
            self._set_run_values(ri, excludes=['labnumber', 'position'])

            if self.aliquot:
                ri.aliquot = int(self.aliquot + i)
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
                    also returns self.frequency if using special labnumber else None
        '''
        freq = self.frequency if self.labnumber in ANALYSIS_MAPPING else None

        if self.template and self.template != NULL_STR and not freq:
            arvs = self._render_template()
        else:
            arvs = self._new_runs()


        if auto_increment:
            if self.position:
                increment = 1
                if ',' in self.position:
                    spos = map(int, self.position.split(','))
                    increment = spos[-1] - spos[0] + 1
                    s = spos[-1]
                else:
                    s = int(self.position)

                e = int(self.endposition)
                if e:
                    self.position = str(e + 1)
                else:
                    self.position = self._increment(self.position, increment=increment)
                if self.endposition:
                    self.endposition = 2 * e + 1 - s

            self.labnumber = self._increment(self.labnumber)


        return arvs, freq

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
    def _new_template(self):
        template = IncrementalHeatTemplate()
        if self.template and self.template != NULL_STR:
            template.load(os.path.join(paths.incremental_heat_template_dir,
                                       '{}.txt'.format(self.template)
                                       )
                          )
        return template

    def _render_template(self):
        arvs = []
        template = self._new_template()

        for st in template.steps:
            if st.is_ok:
                arv = self._new_run(extract_group=self._extract_group_cnt,
                                    step=st.step_id,
                                    position=self.position
                                    )
                arv.trait_set(**st.make_dict())
                arvs.append(arv)

        self._extract_group_cnt += 1

        return arvs

    def _new_runs(self):
        s = 0
        e = 0

        special = self.labnumber in ANALYSIS_MAPPING
        if self.position and not special:
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
                arvs = [self._new_run(position=str(s), special=special)]
#                 self.position = self._increment(self.position)
        elif self.position and self.labnumber == 'dg':
            arvs = [self._new_run(special=False, position=self.position)]

#             self.position = self._increment(self.position)
        else:
            arvs = [self._new_run(special=special)]

        return arvs

    def _increment(self, m, increment=1):

        s = ','
        if s not in m:
            m = (m,)
            s = ''
        else:
            m = m.split(s)
        ms = []
        for mi in m:
            try:
                ms.append(str(int(mi) + increment))
            except ValueError:
                return s.join(m)

        return s.join(ms)

    def _make_irrad_level(self, ln):
        il = ''
        ipos = ln.irradiation_position
        if not ipos is None:
            level = ipos.level
            irrad = level.irradiation
            il = '{}{}'.format(irrad.name, level.name)
        return il

    def _new_run(self, special=False, **kw):
        arv = self._spec_klass(**kw)
        ex = ('extract_value', 'extract_units', 'pattern') if special else tuple()
        if self.labnumber in ('ba', 'bg', 'bc', 'a', 'c'):
            ex += ('position',)


        self._set_run_values(arv, excludes=ex)
        return arv

    def _set_run_values(self, arv, excludes=None):
        if excludes is None:
            excludes = []

        '''
            if run is not an unknown and not a degas then don't copy evalue, eunits and pattern
            if runs is an unknown but is part of an extract group dont copy the evalue
        '''
        if arv.analysis_type != 'unknown':
            if arv.analysis_type != 'dg':
                excludes.extend('extract_value', 'extract_units', 'pattern')
        else:
            if arv.extract_group:
                excludes.extend('extract_value')

        for attr in ('labnumber',
                     'extract_value', 'extract_units', 'cleanup', 'duration',
                     'pattern',
                     'weight', 'comment',
                     'sample', 'irradiation',
                     'skip', 'mass_spectrometer', 'extract_device'

                     ):

            if attr in excludes:
                continue

            setattr(arv, attr, getattr(self, attr))
            setattr(arv, '_prev_{}'.format(attr), getattr(self, attr))

        if self.user_defined_aliquot:
            arv.user_defined_aliquot = True
            arv.aliquot = int(self.aliquot)

        for si in SCRIPT_KEYS:
            name = '{}_script'.format(si)
            if name in excludes or si in excludes:
                continue
            s = getattr(self, name)
            setattr(arv, name, s.name)

    def _clone_run(self, run, excludes=None):
        if excludes is None:
            excludes = []
        for attr in ('labnumber',
                     'extract_value', 'extract_units', 'cleanup', 'duration',
                     'pattern',
                     'position',
                     'weight', 'comment',
                     ):
            if attr in excludes:
                continue
            setattr(self, attr, getattr(run, attr))

        if run.user_defined_aliquot:
            self.aliquot = int(run.aliquot)

        for si in SCRIPT_KEYS:
            name = '{}_script'.format(si)
            s = getattr(run, name)
            if name in excludes or si in excludes:
                continue

            setattr(self, name, Script(name=s,
                                       label=si,
                                       application=self.application,
                                       mass_spectrometer=self.mass_spectrometer))

    def _load_extraction_info(self, script=None):
        if script is None:
            script = self.extraction_script

        if '##' in self.labnumber:
            mod = script.get_parameter('modifier')
            if mod is not None:
                self.labnumber = self.labnumber.replace('##', str(mod))


    def _set_cb_defaults(self, run):
        if run.analysis_type == 'unknown':
            if not run.extract_group:
                self.cb_extract_value = True
                self.cb_extract_units = True
                self.cb_duration = True
                self.cb_cleanup = True
                self.cb_pattern = True
#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('_selected_runs')
    def _selected_runs_handler(self):
        if self._selected_runs:

            self._set_cb_defaults(self._selected_runs[0])
#            self._suppress_cb_change = False
        else:
            td = self.traits()
            for tr in td:
                if tr.startswith('cb_'):
                    td[tr] = False
#            self.cb_position = False

    @on_trait_change('cb_+')
    def _edit_cb_handler(self, name, new):
        if name == 'cbs_enabled':
            return

        def setvalue(obj, attr, v):
#            try:
            pattr = '_prev_{}'.format(nname)
            setattr(obj, pattr, getattr(obj, attr))
            setattr(obj, attr, v)
#            except Exception:
#                setattr(obj, attr, 0)

        if self._selected_runs:
            nname = name[3:]
            if new:
                v = getattr(self, nname)
                for si in self._selected_runs:
                    setvalue(si, nname, v)
            else:
                pname = '_prev_{}'.format(nname)
                for si in self._selected_runs:
                    if hasattr(si, pname):
                        v = getattr(si, pname)
                        setvalue(si, nname, v)
#                    else:
#                        v = ''



    @on_trait_change('''cleanup, duration, extract_value,
extract_units,
pattern,
position''')
    def _edit_handler(self, name, new):
        if self._selected_runs:
            cb = True
            cbname = 'cb_{}'.format(name)
            if hasattr(self, cbname):
                cb = getattr(self, cbname)
            if cb:
                for si in self._selected_runs:
#                    setattr(si, '_prev_{}'.format(name), getattr(si, name))
                    setattr(si, name, new)



    @on_trait_change('''measurement_script:name, 
extraction_script:name, 
post_measurement_script:name,
post_equilibration_script:name
    ''')
    def _edit_script_handler(self, obj, name, new):
        if obj.label == 'Extraction':
            self._load_extraction_info(obj)

        if self._selected_runs:
            for si in self._selected_runs:
                name = '{}_script'.format(obj.label)
                setattr(si, name, new)

    def __labnumber_changed(self):
        if self._labnumber != NULL_STR:
            self.labnumber = self._labnumber

    def _project_changed(self):
        self._clear_labnumber()

    def _selected_irradiation_changed(self):
        self._clear_labnumber()

    def _selected_level_changed(self):
        self._clear_labnumber()

    def _clear_labnumber(self):
        self.labnumber = ''
        self._labnumber = NULL_STR

    def _special_labnumber_changed(self):
        if self.special_labnumber != NULL_STR:
            ln = convert_special_name(self.special_labnumber)
            if ln:
                db = self.db
                if not db:
                    return

                ms = db.get_mass_spectrometer(self.mass_spectrometer)
                ed = db.get_extraction_device(self.extract_device)
                if ln in ('a', 'ba'):
                    ln = make_standard_identifier(ln, '##', ms.id)
                else:
                    ln = make_special_identifier(ln, ed.id, ms.id)

                self.labnumber = ln
                self._load_extraction_info()

                self._labnumber = NULL_STR
            self._frequency_enabled = True
        else:
            self._frequency_enabled = False

    def _aliquot_changed(self):
        if self.aliquot != self.o_aliquot and self.o_aliquot:
            self.user_defined_aliquot = True
        else:
            self.user_defined_aliquot = False

    def _labnumber_changed(self, old, new):
        def _load_scripts(_old, _new):
            '''
                load default steps if 
                    1. labnumber is special
                    2. labnumber was a special and now unknown
                    
                dont load if was unknown and now unknown
                this preserves the users changes 
            '''
            # if new is special e.g bu-01-01
            if '-' in _new:
                _new = _new.split('-')[0]
            if '-' in _old:
                _old = old.split('-')[0]

            if _new in ANALYSIS_MAPPING or \
                _old in ANALYSIS_MAPPING or not _old and _new:
                # set default scripts
                self._load_default_scripts(key=_new)

        labnumber = self.labnumber
        if not labnumber or labnumber == NULL_STR:
            return

        db = self.db
        if not db:
            return

        special = False
        try:
            _ = int(labnumber)
        except ValueError:
            special = True

        # if labnumber has a place holder load default script and return
        if '##' in labnumber:
            _load_scripts(old, new)
            return

        self.irradiation = ''
        self.sample = ''

        if labnumber:
            # convert labnumber (a, bg, or 10034 etc)
#            clabnumber = convert_identifier(labnumber)
            ln = db.get_labnumber(labnumber)
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

                self.irradiation = self._make_irrad_level(ln)
                _load_scripts(old, new)

            elif special:
                if self.confirmation_dialog('Lab Identifer {} does not exist. Would you like to add it?'.format(labnumber)):
                    db.add_labnumber(labnumber)
                    db.commit()
                else:
                    self.labnumber = ''
            else:
                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))

    def _edit_template_fired(self):
        temp = self._new_template()
        self.open_view(temp)

#===============================================================================
# property get/set
#===============================================================================
    def _get_cbs_enabled(self):
        return self._selected_runs

    def _get_extractable(self):
        ln = self.labnumber
        if '-' in ln:
            ln = ln.split('-')[0]

        return not ln in NON_EXTRACTABLE

    @cached_property
    def _get_irradiations(self):
#        return {'a':'1:xxx','g':'2:bbb',}
        if self.db:
            keys = [(pi, pi.name) for pi in self.db.get_irradiations()]
            keys = [(a, '{:02n}:{}'.format(i + 1, b)) for i, (a, b) in enumerate(keys)]
            keys = [(NULL_STR, '00:{}'.format(NULL_STR))] + keys
            return dict(keys)
        else:
            return dict()

    @cached_property
    def _get_levels(self):
        if self.db:
            irrad = self.db.get_irradiation(self.selected_irradiation)
            r = [(NULL_STR, '00:{}'.format(NULL_STR))]
            if irrad:
                rr = sorted(((pi, pi.name) for pi in irrad.levels), key=lambda p: p[1])
                rr = [(a, '{:02n}:{}'.format(i + 1, b)) for i, (a, b) in enumerate(rr)]
                r.extend(rr)

            return dict(r)
        else:
            return dict()

    @cached_property
    def _get_projects(self):

        if self.db:
            keys = [(pi, pi.name) for pi in self.db.get_projects()]
            keys = [(NULL_STR, NULL_STR)] + keys
            return dict(keys)
        else:
            return dict()

    @cached_property
    def _get_labnumbers(self):
        lns = []
        if self.selected_level and self.selected_level != NULL_STR:
            lns = [str(pi.labnumber.identifier)
                    for pi in self.selected_level.positions]
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

    def _get_edit_template_label(self):
        return 'Edit' if self.template and self.template != NULL_STR else 'New'

    @cached_property
    def _get_patterns(self):
        p = paths.pattern_dir
        extension = '.lp,.txt'
        return self._ls_directory(p, extension)

    @cached_property
    def _get_templates(self):
        p = paths.incremental_heat_template_dir
        extension = '.txt'
        return self._ls_directory(p, extension)

    def _ls_directory(self, p, extension):
        ps = [NULL_STR]
        def test(path):
            return any([path.endswith(ext) for ext in extension.split(',')])

        if os.path.isdir(p):
            ds = os.listdir(p)
            if extension is not None:
                ds = [pi for pi in ds
                            if test(pi)]
            ds = [os.path.splitext(pi)[0] for pi in ds]
            ps += ds

        return ps

#===============================================================================
# groups
#===============================================================================
    def _frequency_group(self):
        grp = Group(Item('frequency'))
        return grp

    def _get_info_group(self):
        grp = Group(
                   Item('project', editor=EnumEditor(name='projects'),
                       ),
                   HGroup(
                          Item('selected_irradiation',
                               label='Irradiation',
                               editor=EnumEditor(name='irradiations')),
                          Item('selected_level',
                               label='Level',
                               editor=EnumEditor(name='levels')),
                          ),

                   HGroup(Item('special_labnumber', editor=EnumEditor(values=SPECIAL_NAMES),
                               ),
                          Item('frequency')
                          ),
                   HGroup(Item('labnumber',
                              tooltip='Enter a Labnumber'
                              ),
                          Item('_labnumber', show_label=False,
                              editor=EnumEditor(name='labnumbers'),
                              width=100,
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
                   CBItem('weight',
                        label='Weight (mg)',
                        tooltip='(Optional) Enter the weight of the sample in mg. Will be saved in Database with analysis'
                        ),
                   CBItem('comment',
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
                         HGroup(CBItem('position',
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
                                    CBItem('extract_value', label='Extract',
                                         tooltip='Set the extract value in extract units',
                                         enabled_when='extractable'
                                         ),
                                    CBItem('extract_units',
                                            show_label=False,
                                            editor=EnumEditor(name='extract_units_names')),
                                    spring,
                                    Label('Step Heat Template'),
                                    UItem('template', editor=EnumEditor(name='templates')),
                                    UItem('edit_template',
                                          editor=ButtonEditor(label_value='edit_template_label')
                                          ),
                                    ),
                             CBItem('duration', label='Duration (s)',
                                  tooltip='Set the number of seconds to run the extraction device.'

                                  ),
                             CBItem('cleanup', label='Cleanup (s)',
                                  tooltip='Set the number of seconds to getter the sample gas'
                                  ),
                             # Item('ramp_rate', label='Ramp Rate (C/s)'),
                             CBItem('pattern', editor=EnumEditor(name='patterns')),
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
                        pos_grp,
                        extract_grp,
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
