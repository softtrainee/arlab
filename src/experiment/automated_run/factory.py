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
from src.constants import NULL_STR, SCRIPT_KEYS, SCRIPT_NAMES, LINE_STR
from src.experiment.utilities.identifier import SPECIAL_NAMES, SPECIAL_MAPPING, \
    convert_identifier, convert_special_name, ANALYSIS_MAPPING, NON_EXTRACTABLE, \
    make_special_identifier, make_standard_identifier
from src.experiment.automated_run.spec import AutomatedRunSpec
from src.regex import TRANSECT_REGEX, POSITION_REGEX
# from src.experiment.utilities.script_mixin import ScriptMixin
from src.paths import paths
from src.experiment.script.script import Script
from src.experiment.queue.increment_heat_template import IncrementalHeatTemplate
from src.viewable import Viewable
from src.ui.thread import Thread
from src.loggable import Loggable
import yaml
from src.experiment.utilities.human_error_checker import HumanErrorChecker
from src.helpers.filetools import list_directory
from src.lasers.pattern.pattern_maker_view import PatternMakerView


def EKlass(klass):
    return klass(enter_set=True, auto_set=False)

# class AutomatedRunFactory(Viewable, ScriptMixin):
class AutomatedRunFactory(Viewable):
    db = Any

    labnumber = String(enter_set=True, auto_set=False)

#    aliquot = Property(Int(enter_set=True, auto_set=False), depends_on='_aliquot')
#    _aliquot = Int
#    o_aliquot = Int
    aliquot = EKlass(Int)
    user_defined_aliquot = False
    special_labnumber = Str('Special Labnumber')

    _labnumber = Str
    labnumbers = Property(depends_on='project, selected_level')

    project = Any
    projects = Property(depends_on='db')

    selected_irradiation = Str('Irradiation')
    irradiations = Property(depends_on='db')
    selected_level = Str('Level')
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
    extract_value = Property(
                             EKlass(Float),
                             depends_on='_extract_value')
    _extract_value = Float
    extract_units = Str(NULL_STR)
    extract_units_names = List(['', 'watts', 'temp', 'percent'])
    _default_extract_units = 'watts'

    extract_group = Int(enter_set=True, auto_set=False)
    extract_group_button = Button('Group Selected')

    ramp_duration = EKlass(Float)

    duration = EKlass(Float)
    cleanup = EKlass(Float)
    beam_diameter = Property(EKlass(Str), depends_on='beam_diameter')
    _beam_diameter = Any

    pattern = Str
    patterns = List
#     patterns = Property(depends_on='_patterns')
#     _patterns = List

    edit_pattern = Event
    edit_pattern_label = Property(depends_on='pattern')
    #===========================================================================
    # templates
    #===========================================================================
    template = String('Step Heat Template')
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
    refresh_table_needed = Event
    changed = Event
    suppress_update = False
#    clear_selection = Event

    edit_mode = Bool(False)
    edit_mode_label = Property(depends_on='edit_mode')
    edit_enabled = Bool(False)


    mass_spectrometer = String
    extract_device = Str

    extraction_script = Instance(Script)
    measurement_script = Instance(Script)
    post_measurement_script = Instance(Script)
    post_equilibration_script = Instance(Script)

#     def _template_changed(self):
#         print self, self.template
    human_error_checker = Instance(HumanErrorChecker, ())

    _update_thread = None

    def check_run_addition(self, runs, load_name):
        '''
            check if its ok to add runs to the queue.
            ie. do they have any missing values.
                does the labnumber match the loading
            
            return True if ok to add runs else False
        '''
        hec = self.human_error_checker
        ret = hec.check(runs, test_all=True)
        if ret:
            hec.report_errors(ret)
            return False

        return True

    def load_templates(self):
        self.templates = self._get_templates()
    
    def load_patterns(self, ps):
        self.patterns=self._get_patterns(ps)
        
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

    def new_runs(self, positions=None, auto_increment_position=False,
                    auto_increment_id=False,
                    extract_group_cnt=0):
        '''
            returns a list of runs even if its only one run 
                    also returns self.frequency if using special labnumber else None
        '''
        _ln, special = self._make_short_labnumber()

        freq = self.frequency if special else None

        if self._use_template() and not freq and not special:
#        if self.template and self.template  and not freq and not special :
            arvs = self._render_template(extract_group_cnt)
        else:
            arvs = self._new_runs(positions=positions)

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
    def _new_pattern(self):
        pm = PatternMakerView()

        if self._use_pattern():
            if pm.load_pattern(self.pattern):
                return pm
        else:
            return pm

    def _new_template(self):
        template = IncrementalHeatTemplate()
        if self._use_template():
            t=self.template
            if not t.endswith('.txt'):
                t='{}.txt'.format(t)
            t=os.path.join(paths.incremental_heat_template_dir, t)
            template.load(t)
            
        return template

    def _render_template(self, cnt):
        arvs = []
        template = self._new_template()

        for st in template.steps:
            if st.value or st.duration or st.cleanup:
                arv = self._new_run(extract_group=cnt + 1,
                                    step=st.step_id,
                                    position=self.position
                                    )
                arv.trait_set(**st.make_dict(self.duration, self.cleanup))
                arvs.append(arv)

#        self._extract_group_cnt += 1
        return arvs

    def _new_runs(self, positions):
        s = 0
        e = 0
        _ln, special = self._make_short_labnumber()
        if special:
            arvs = [self._new_run()]
        else:
            if positions:
                arvs = [self._new_run(position=pi, excludes=['position'])
                                        for pi in positions]
            elif self.position:

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
            excludes.extend(('extract_value', 'extract_units', 'pattern', 'beam_diameter'))
            if arv.analysis_type == 'pause':
                excludes.extend(('cleanup', 'position'))
        elif arv.analysis_type not in ('unknown', 'degas'):
            excludes.extend(('position', 'extract_value', 'extract_units', 'pattern',
                             'cleanup', 'duration', 'beam_diameter'
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
                     'pattern', 'beam_diameter',
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
                     'extract_group',
                     'pattern', 'beam_diameter',
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
    def _extract_group_button_fired(self):
        if self.edit_mode and \
            self._selected_runs and \
                not self.suppress_update:

            eg = self._selected_runs[0].extract_group + 1
            self.extract_group = eg

    @on_trait_change('''cleanup, duration, extract_value,ramp_duration,
extract_units,
pattern,
position,
weight, comment, skip, end_after, extract_group''')
    def _edit_handler(self, name, new):
        self._update_run_values(name, new)

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
            self.refresh_table_needed = True

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
        if not self.special_labnumber in ('Special Labnumber', LINE_STR):
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
                        ln = make_special_identifier(ln, edname, msname)

                self.labnumber = ln
                self._load_extraction_info()

                self._labnumber = NULL_STR
            self._frequency_enabled = True
#            self.clear_selection = True
        else:
            self._frequency_enabled = False

    def _labnumber_changed(self, old, new):
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
            self._load_scripts(old, new)
            return

        self.irradiation = ''
        self.sample = ''

        self._aliquot = 0
        if labnumber:
            # convert labnumber (a, bg, or 10034 etc)
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

                self.irradiation = self._make_irrad_level(ln)
                self._load_scripts(old, new)

            elif special:
                ln = labnumber[:2]
                if ln == 'dg':
                    self._load_extraction_defaults(ln)

                if not (ln in ('pa', 'dg')):
                    '''
                        don't add pause or degas to database
                    '''
                    if self.confirmation_dialog('Lab Identifer {} does not exist. Would you like to add it?'.format(labnumber)):
                        db.add_labnumber(labnumber)
                        db.commit()
                        self._aliquot = 1
                        self._load_scripts(old, new)
                    else:
                        self.labnumber = ''
                else:
                    self._load_scripts(old, new)
            else:
                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))

    def _template_closed(self):
        self.load_templates()
        self.template = os.path.splitext(self._template.name)[0]
        del self._template

    def _pattern_closed(self):
        self.load_patterns()
        self.pattern = os.path.splitext(self._pattern.name)[0]
        del self._pattern


    def _edit_template_fired(self):
        temp = self._new_template()
        temp.on_trait_change(self._template_closed, 'close_event')
        self.open_view(temp)
        self._template = temp

    def _edit_pattern_fired(self):
        pat = self._new_pattern()
        pat.on_trait_change(self._pattern_closed, 'close_event')
        self.open_view(pat)
        self._pattern = pat

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
#         if self.db:
#             keys = [(pi, pi.name) for pi in self.db.get_irradiations()]
#             keys = [(a, '{:02n}:{}'.format(i + 2, b)) for i, (a, b) in enumerate(keys)]
#             keys = [
#                     ('Irradiation', '00:Irradiation'.format(NULL_STR)),
#                     (LINE_STR, '01:{}'.format(LINE_STR)),
#                     ] + keys
#             return dict(keys)
#         else:
#             return dict()

        irradiations = []
        if self.db:
            irradiations = [pi.name for pi in self.db.get_irradiations()]

        return ['Irradiation', LINE_STR] + irradiations

    @cached_property
    def _get_levels(self):
        levels = []
        if self.db:
            if not self.selected_irradiation in ('IRRADIATION', LINE_STR):
                irrad = self.db.get_irradiation(self.selected_irradiation)
                if irrad:
                    levels = sorted([li.name for li in irrad.levels])
        if levels:
            self.selected_level = levels[0] if levels else 'LEVEL'

        return ['Level', LINE_STR] + levels
#         if self.db:
#             r = [
#                  ('Level', '00:Level'.format(NULL_STR)),
#                  (LINE_STR, '01:{}'.format(LINE_STR)),
#                  ]

#             if self.selected_irradiation and self.selected_irradiation != 'Irradiation':
#                 irrad = self.db.get_irradiation(self.selected_irradiation)
#                 if irrad:
#                     rr = sorted(((pi, pi.name) for pi in irrad.levels), key=lambda p: p[1])
#                     rr = [(a, '{:02n}:{}'.format(i + 1, b)) for i, (a, b) in enumerate(rr)]
#                     r.extend(rr)
#
#             return dict(r)
#         else:
#             return dict()

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
        db = self.db
        if db:
            if self.selected_level and not self.selected_level in ('Level', LINE_STR):
                level = db.get_irradiation_level(self.selected_irradiation,
                                                 self.selected_level)
                if level:
                    lns = [str(pi.labnumber.identifier)
                        for pi in level.positions]


        return sorted(lns)
#         if self.selected_level and not self.selected_level in ('Level', LINE_STR):
#             lns = [str(pi.labnumber.identifier)
#                     for pi in self.selected_level.positions]

#         project = self.project
#         if project and project != NULL_STR:
#             project = self.db.get_project(project)
#             if project is not None:
#                 lns = [str(ln.identifier)
#                     for s in project.samples
#                         for ln in s.labnumbers]
#         return sorted(lns)
#        return [NULL_STR] + sorted(lns)

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

    def _get_edit_pattern_label(self):
        return 'Edit' if self._use_pattern() else 'New'

    def _use_pattern(self):
        return self.pattern and not self.pattern in (LINE_STR,)

    def _use_template(self):
        return self.template and not self.template in ('Step Heat Template', LINE_STR)

    def _get_edit_template_label(self):
        return 'Edit' if self._use_template() else 'New'
    
    def _get_patterns(self, ps):
        p = paths.pattern_dir
        extension = '.lp'
        patterns = list_directory(p, extension)
        return ['', ] + ps + [LINE_STR] + patterns

    def _get_templates(self):
        p = paths.incremental_heat_template_dir
        extension = '.txt'
        temps = list_directory(p, extension)
        if self.template in temps:
            self.template = temps[temps.index(self.template)]
        else:
            self.template = 'Step Heat Template'

        return ['Step Heat Template', LINE_STR] + temps
    
    def _aliquot_changed(self):
        if self.edit_mode:
            for si in self._selected_runs:
                if si.aliquot != self.aliquot:
                    si.user_defined_aliquot = True
                    si.assigned_aliquot = int(self.aliquot)
#                else:
#                    si.user_defined_aliquot = self.user_defined_aliquot
#
#                if si.user_defined_aliquot:
#                    si.aliquot = int(self.aliquot)

            self.update_info_needed = True

    def _get_beam_diameter(self):
        bd = ''
        if self._beam_diameter is not None:
            bd = self._beam_diameter
        return bd

    def _set_beam_diameter(self, v):
        try:
            self._beam_diameter = float(v)
            self._update_run_values('beam_diameter', self._beam_diameter)
        except (ValueError, TypeError):
            pass

    def _update_run_values(self, attr, v):
        def func():
            for si in self._selected_runs:
                setattr(si, attr, v)

            if attr == 'extract_group':
                self.update_info_needed = True

            self.changed = True
            self.refresh_table_needed = True

        if self.edit_mode and \
            self._selected_runs and \
                not self.suppress_update:

            if self._update_thread:
                self._update_thread.join()

            t = Thread(target=func)
            self._update_thread = t
            t.start()

#===============================================================================
#
#===============================================================================
    def _load_extraction_defaults(self, ln):
        defaults = self._load_default_file()
        if defaults:
            if ln in defaults:
                grp = defaults[ln]
                for attr in ('extract_value', 'extract_units'):
                    v = grp.get(attr)
                    if v is not None:
                        setattr(self, attr, v)

    def _load_scripts(self, old, new):
        '''
            load default scripts if 
                1. labnumber is special
                2. labnumber was a special and now unknown
                
            dont load if was unknown and now unknown
            this preserves the users changes 
        '''
        # if new is special e.g bu-01-01
        if '-' in new:
            new = new.split('-')[0]
        if '-' in old:
            old = old.split('-')[0]

        if new in ANALYSIS_MAPPING or \
            old in ANALYSIS_MAPPING or not old and new:
            # set default scripts
            self._load_default_scripts(new)

    def _load_default_scripts(self, labnumber):
        self.debug('load default scripts for {}'.format(labnumber))
        # if labnumber is int use key='U'
        try:
            _ = int(labnumber)
            labnumber = 'u'
        except ValueError:
            pass

        labnumber = str(labnumber).lower()

        defaults = self._load_default_file()
        if defaults:
            if labnumber in defaults:
                default_scripts = defaults[labnumber]
                for skey in SCRIPT_KEYS:
                    new_script_name = default_scripts.get(skey) or NULL_STR

                    new_script_name = self._remove_file_extension(new_script_name)
                    if labnumber in ('u', 'bu') and self.extract_device != NULL_STR:

                        # the default value trumps pychron's
                        if self.extract_device and new_script_name == NULL_STR:
                            e = self.extract_device.split(' ')[1].lower()
                            if skey == 'extraction':
                                new_script_name = e
                            elif skey == 'post_equilibration':
                                new_script_name = 'pump_{}'.format(e)

                    elif labnumber == 'dg':
                        e = self.extract_device.split(' ')[1].lower()
                        new_script_name = '{}_{}'.format(e, new_script_name)

                    script = getattr(self, '{}_script'.format(skey))
                    script.name = new_script_name

    def _load_default_file(self):
        # open the yaml config file
        p = os.path.join(paths.scripts_dir, 'defaults.yaml')
        if not os.path.isfile(p):
            self.warning('Script defaults file does not exist {}'.format(p))
            return

        with open(p, 'r') as fp:
            defaults = yaml.load(fp)

        # convert keys to lowercase
        defaults = dict([(k.lower(), v) for k, v in defaults.iteritems()])
        return defaults


#===============================================================================
#
#===============================================================================
    def _application_changed(self):
        self.extraction_script.application = self.application
        self.measurement_script.application = self.application
        self.post_measurement_script.application = self.application
        self.post_equilibration_script.application = self.application


    @on_trait_change('mass_spectrometer, can_edit')
    def _update_value(self, name, new):
        for si in SCRIPT_NAMES:
            script = getattr(self, si)
            setattr(script, name, new)

    def _script_factory(self, label, name, kind='ExtractionLine'):
        return Script(label=label,
#                      names=getattr(self, '{}_scripts'.format(name)),
                      application=self.application,
                      mass_spectrometer=self.mass_spectrometer,
                      kind=kind,
#                       can_edit=self.can_edit
                      )

    def _extraction_script_default(self):
        return self._script_factory('Extraction', 'extraction')

    def _measurement_script_default(self):
        return self._script_factory('Measurement', 'measurement', kind='Measurement')

    def _post_measurement_script_default(self):
        return self._script_factory('Post Measurement', 'post_measurement')

    def _post_equilibration_script_default(self):
        return self._script_factory('Post Equilibration', 'post_equilibration')

    def _clean_script_name(self, name):
        name = self._remove_mass_spectrometer_name(name)
        return self._remove_file_extension(name)

    def _remove_file_extension(self, name, ext='.py'):
        if name is NULL_STR:
            return NULL_STR

        if name.endswith('.py'):
            name = name[:-3]

        return name

    def _remove_mass_spectrometer_name(self, name):
        if self.mass_spectrometer:
            name = name.replace('{}_'.format(self.mass_spectrometer), '')
        return name
#============= EOF =============================================



