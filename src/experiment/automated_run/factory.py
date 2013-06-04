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
# from traitsui.api import View, Item, EnumEditor, HGroup, VGroup, Group, Spring, spring, \
#    UItem, ButtonEditor, Label
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


class AutomatedRunFactory(Viewable, ScriptMixin):
    db = Any

    labnumber = String(enter_set=True, auto_set=False)
    
    aliquot=Property(Int(enter_set=True, auto_set=False), depends_on='_aliquot')
    _aliquot=Int
    o_aliquot=Int
    
#     aliquot = Long
#     o_aliquot = Either(Long, Int)
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
    end_after = Bool(False)
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
    # templates
    #===========================================================================
    template = String
    templates = List  # Property(depends_on='update_templates_needed')
#     update_templates_needed = Event
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

    info_label = Property(depends_on='labnumber')
    #===========================================================================
    # private
    #===========================================================================
    _selected_runs = List
    _spec_klass = AutomatedRunSpec
    _extract_group_cnt = 1

#    frequencyable = Property(depends_on='labnumber')
    extractable = Property(depends_on='labnumber')
    update_info_needed = Event
    changed = Event
    suppress_update = False
#    clear_selection = Event

    edit_mode = Bool(False)
    edit_mode_label = Property(depends_on='edit_mode')
    edit_enabled = Bool(False)

#     def _template_changed(self):
#         print self, self.template

    def load_templates(self):
        self.templates = self._get_templates()

    def use_frequency(self):
        return self.labnumber in ANALYSIS_MAPPING and self.frequency

    def load_from_run(self, run):
        self._clone_run(run)

#    def commit_changes(self, runs):
#        for i, ri in enumerate(runs):
#            self._set_run_values(ri, excludes=['labnumber', 'position', 'mass_spectrometer', 'extract_device'])
#
#            if self.aliquot:
#                ri.aliquot = int(self.aliquot + i)
#                ri.user_defined_aliquot = True
#            else:
#                ri.user_defined_aliquot = False

    def set_selected_runs(self, runs):
        if runs:
            run = runs[0]
            self._clone_run(run)

        self._selected_runs = runs
        self.suppress_update = False
        if not runs:
            self.edit_mode = False
            self.edit_enabled = False
        elif len(runs) == 1:
            self.edit_enabled = True
        else:
            self.edit_enabled = False
            self.edit_mode = True

    def _make_short_labnumber(self, labnumber=None):
        if labnumber is None:
            labnumber = self.labnumber
        if '-' in labnumber:
            labnumber = labnumber.split('-')[0]

        special = labnumber in ANALYSIS_MAPPING
        return labnumber, special

    def new_runs(self, auto_increment_position, auto_increment_id=False):
        '''
            returns a list of runs even if its only one run 
                    also returns self.frequency if using special labnumber else None
        '''
        _ln, special = self._make_short_labnumber()

        freq = self.frequency if special else None

        if self.template and self.template != NULL_STR and not freq and not special :
            arvs = self._render_template()
        else:
            arvs = self._new_runs()

        if auto_increment_id:
            self.labnumber = self._increment(self.labnumber)

        if auto_increment_position:
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
            if st.value or st.duration or st.cleanup:
                arv = self._new_run(extract_group=self._extract_group_cnt,
                                    step=st.step_id,
                                    position=self.position
                                    )
                arv.trait_set(**st.make_dict(self.duration, self.cleanup))
                arvs.append(arv)

        self._extract_group_cnt += 1
        return arvs

    def _new_runs(self):
        s = 0
        e = 0
        _ln, special = self._make_short_labnumber()
        if special:
            arvs = [self._new_run()]
        else:
            if self.position:

                # is position a int or list of ints
                if ',' in self.position:
                    s = int(self.position.split(',')[0])
                else:
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
                        arvs.append(self._new_run(position=position, excludes=['position']))
                        '''
                            clear user_defined_aliquot flag
                            if adding multiple runs this allows 
                            the subsequent runs to have there aliquots defined by db
                        '''
                        self.user_defined_aliquot = False

                else:
                    arvs = [self._new_run()]
            else:
                arvs = [self._new_run()]
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
        if ipos is not None:
            level = ipos.level
            irrad = level.irradiation
            il = '{}{} {}'.format(irrad.name, level.name, ipos.position)
        return il

    def _new_run(self, excludes=None, **kw):

        # need to set the labnumber now because analysis_type depends on it
        arv = self._spec_klass(labnumber=self.labnumber, **kw)

        if excludes is None:
            excludes = []

        if arv.analysis_type in ('blank_unknown', 'pause'):
            excludes.extend(('extract_value', 'extract_units', 'pattern'))
            if arv.analysis_type == 'pause':
                excludes.extend(('cleanup', 'position'))
        elif arv.analysis_type not in ('unknown', 'degas'):
            excludes.extend(('position', 'extract_value', 'extract_units', 'pattern',
                             'cleanup', 'duration',
                             ))

        self._set_run_values(arv, excludes=excludes)
        return arv

    def _set_run_values(self, arv, excludes=None):
        if excludes is None:
            excludes = []


        '''
            if run is not an unknown and not a degas then don't copy evalue, eunits and pattern
            if runs is an unknown but is part of an extract group dont copy the evalue
        '''

        for attr in (
                     'position',
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
            self.debug('setting user defined aliquot')
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
                if isinstance(mod, int):
                    mod = '{:02n}'.format(mod)

                self.labnumber = self.labnumber.replace('##', str(mod))


#===============================================================================
# handlers
#===============================================================================

    @on_trait_change('''cleanup, duration, extract_value,
extract_units,
pattern,
position,
weight, comment, skip, end_after''')
    def _edit_handler(self, name, new):
        if self.edit_mode and \
            self._selected_runs and \
                not self.suppress_update:

            for si in self._selected_runs:
                setattr(si, name, new)
            self.changed = True

    @on_trait_change('''measurement_script:name, 
extraction_script:name, 
post_measurement_script:name,
post_equilibration_script:name
    ''')
    def _edit_script_handler(self, obj, name, new):
        if self.edit_mode and not self.suppress_update:
            if obj.label == 'Extraction':
                self._load_extraction_info(obj)

            if self._selected_runs:
                for si in self._selected_runs:
                    name = '{}_script'.format(obj.label)
                    setattr(si, name, new)
            self.changed = True

    def _skip_changed(self):
        self.update_info_needed = True

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
                if ln in ('dg', 'pa'):
                    pass
                else:
                    db = self.db
                    if not db:
                        return

                    ms = db.get_mass_spectrometer(self.mass_spectrometer)
                    ed = db.get_extraction_device(self.extract_device)
                    if ln in ('a', 'ba', 'c', 'bc'):
                        ln = make_standard_identifier(ln, '##', ms.name[0].capitalize())
                    else:
                        msname = ms.name[0].capitalize()
                        edname = ''.join(map(lambda x:x[0].capitalize(), ed.name.split(' ')))
    #                     ln = make_special_identifier(ln, ed.id, ms.id)
                        ln = make_special_identifier(ln, edname, msname)

                self.labnumber = ln
                self._load_extraction_info()

                self._labnumber = NULL_STR
            self._frequency_enabled = True
#            self.clear_selection = True
        else:
            self._frequency_enabled = False

#     def _aliquot_changed(self):
#         if self.edit_mode:
#             if self.aliquot:
#                 pass
#                 if self.aliquot != self.o_aliquot and self.o_aliquot:
#                     self.user_defined_aliquot = True
#                 else:
#                     self.user_defined_aliquot = False
# 
#                 for si in self._selected_runs:
# 
#                     if si.aliquot != self.aliquot:
#                         si.user_defined_aliquot = True
#                     else:
#                         si.user_defined_aliquot = self.user_defined_aliquot
# 
#                     if si.user_defined_aliquot:
#                         si.aliquot = int(self.aliquot)
#
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
                self._load_default_scripts(_new)

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
        
        self._aliquot=0
#         self.aliquot = 0
        self.o_aliquot = 0
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
                    a = int(ln.analyses[-1].aliquot + 1)
                except IndexError, e:
                    a = 1

                self._aliquot = a
                self.o_aliquot = a
#                 self.aliquot = a

                self.irradiation = self._make_irrad_level(ln)
                _load_scripts(old, new)

            elif special:
                if not (labnumber[:2] in ('pa', 'dg')):
                    '''
                        don't add pause or degas to database
                    '''
                    if self.confirmation_dialog('Lab Identifer {} does not exist. Would you like to add it?'.format(labnumber)):
                        db.add_labnumber(labnumber)
                        db.commit()
                        self._aliquot = 1
                        _load_scripts(old, new)
                    else:
                        self.labnumber = ''
                else:
                    _load_scripts(old, new)
            else:
                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))

    def _template_closed(self):
        self.templates = self.load_templates()
        self.template = os.path.splitext(self._template.name)[0]
#        self.update_templates_needed = True
        del self._template

    def _edit_template_fired(self):
        temp = self._new_template()
        temp.on_trait_change(self._template_closed, 'close_event')
        self.open_view(temp)
        self._template = temp

    def _edit_mode_button_fired(self):
        self.edit_mode = not self.edit_mode
#===============================================================================
# property get/set
#===============================================================================
    def _get_edit_mode_label(self):
        return 'Editing' if self.edit_mode else ''

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

        project = self.project
        if project and project != NULL_STR:
            project = self.db.get_project(project)
            if project is not None:
                lns = [str(ln.identifier)
                    for s in project.samples
                        for ln in s.labnumbers]

        return [NULL_STR] + sorted(lns)

    def _get_position(self):
        return self._position

    def _set_position(self, pos):
        self._position = pos

    def _get_info_label(self):
        return '{} {} {}'.format(self.labnumber, self.irradiation, self.sample)

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

#     @cached_property
    def _get_templates(self):
        p = paths.incremental_heat_template_dir
        extension = '.txt'
        temps = self._ls_directory(p, extension)
        if self.template in temps:
            self.template = temps[temps.index(self.template)]
        else:
            self.template = NULL_STR
        return temps

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
    
    
    def _set_aliquot(self, a):
        if a!=self.o_aliquot:
            self.user_defined_aliquot=True
        
        if self.edit_mode:                    
            for si in self._selected_runs:
                if si.aliquot != a:
                    si.user_defined_aliquot = True
                else:
                    si.user_defined_aliquot = self.user_defined_aliquot
# 
                if si.user_defined_aliquot:
                    si.aliquot = int(a)
            self.update_info_needed=True
      
        self.o_aliquot=self._aliquot
        self._aliquot=int(a)
        
    def _get_aliquot(self):
        return self._aliquot
            
#============= EOF =============================================



