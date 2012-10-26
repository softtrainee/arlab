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
from traits.api import HasTraits, Property, Str, cached_property, \
    List, on_trait_change, Int, Bool, Event, Any, Button, Undefined, Float
from traitsui.api import View, Item, EnumEditor, \
     VGroup, HGroup, Spring, spring, Group, Image, ImageEditor, TabularEditor, \
     Handler

from traitsui.tabular_adapter import TabularAdapter
from pyface.image_resource import ImageResource

#============= standard library imports ========================
import os
import struct
#============= local library imports  ==========================
from src.loggable import Loggable
from src.paths import paths
from src.experiment.entry.irradiation import Irradiation


ALPHAS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHAS = [a for a in ALPHAS] + ['{}{}'.format(a, b)
                                    for a in ALPHAS
                                        for b in ALPHAS]
class Level(HasTraits):
    name = Str
    tray = Str
    trays = List
    def traits_view(self):
        v = View(HGroup(Item('name'), Item('tray', show_label=False, editor=EnumEditor(name='trays'))),
                 buttons=['OK', 'Cancel']
                 )
        return v

    def _tray_default(self):
        return self.trays[0]

class IrradiatedSample(HasTraits):
    labnumber = Str
    material = Str
    sample = Str
    hole = Int
    project = Str
    size = Str
    weight = Str
    note = Str
    j = Float
    j_err = Float

    auto_assigned = Bool(False)
#
    @on_trait_change('labnumber,sample, project, material')
    def _update_auto_assigned(self, obj, name, old, new):
#        print 'ol', name, old, new
        if old:
            self.auto_assigned = False

class IrradiatedSampleAdapter(TabularAdapter):
    columns = [
               ('Hole', 'hole'),
               ('Labnumber', 'labnumber'),
               ('Sample', 'sample'),
               ('Project', 'project'),
               ('Material', 'material'),
               ('Size', 'size'),
               ('Weight', 'weight'),
               ('J', 'j'),
               (u'\u00b1', 'j_err'),
               ('Note', 'note')
             ]
#    hole_can_edit = False
    hole_width = Int(45)
#    def _get_hole_width(self):
#        return 35

    def get_bg_color(self, obj, trait, row):
        item = getattr(obj, trait)[row]
        if item.auto_assigned:
            return '#B0C4DE'

class LabnumberEntry(Loggable):
    db = Any
    irradiation = Str
    level = Str
    irradiation_tray = Str

    irradiations = Property(depends_on='saved')
    levels = Property(depends_on='irradiation,saved')
    trays = Property

    saved = Event
#    irradiation_trays = Property
    tray_name = Str
    irradiation_tray_image = Property(Image, depends_on='level, irradiation')

    irradiated_samples = List(IrradiatedSample)

    auto_assign = Bool
    auto_startrid = Int(19999)
    auto_assign_overwrite = Bool(False)
    auto_project = Str('Foo')
    auto_sample = Str('FC-2')
    auto_material = Str('sanidine')
    auto_j = Float(1e-4)
    auto_j_err = Float(1e-7)
    freeze_button = Button('Freeze')
    thaw_button = Button('Thaw')

    _update_sample_table = Event

    save_button = Button('Save')
    add_irradiation_button = Button('Add Irradiation')
    add_level_button = Button('Add Level')


    selected = Any

    def __init__(self, *args, **kw):
        super(LabnumberEntry, self).__init__(*args, **kw)
        self._load_default_holders()

    def _load_default_holders(self):
        db = self.db
        for t in self.trays:
            p = os.path.join(self._get_map_path(), t)
            with open(p, 'r') as f:
                h = f.readline()
                nholes, _diam = h.split(',')
                nholes = int(nholes)
                holes = [map(float, l.strip().split(',')) for i, l in enumerate(f) if i < nholes]
                blob = ''.join([struct.pack('>ff', x, y) for x, y in holes])
                db.add_irradiation_holder(t, geometry=blob)

        db.commit()

    def _set_auto_params(self, s, rid):
        s.labnumber = rid
        s.sample = self.auto_sample
        s.project = self.auto_project
        s.material = self.auto_material
        s.j = self.auto_j
        s.j_err = self.auto_j_err

    def _load_irradiated_samples(self, name):

        p = os.path.join(self._get_map_path(), name)
        self.irradiated_samples = []
        with open(p, 'r') as f:
            line = f.readline()
            nholes, diam = line.split(',')
            for ni in range(int(nholes)):
                self.irradiated_samples.append(IrradiatedSample(hole=ni + 1))

    def _db_default(self):
        #=======================================================================
        # debug
        #=======================================================================
        from src.database.adapters.isotope_adapter import IsotopeAdapter
        db = IsotopeAdapter(name='isotopedb_dev_migrate',
                          username='root',
                          host='localhost',
                          kind='mysql',
                          password='Argon'
                          )
        db.connect()
        return db
        #=======================================================================
        # 
        #=======================================================================
    def _save_to_db(self):
        db = self.db

        for irs in self.irradiated_samples:
            ln = irs.labnumber
            if not ln:
                continue

            sam = irs.sample
            proj = irs.project
            mat = irs.material
            if proj:
                proj = db.add_project(proj)

            if mat:
                mat = db.add_material(mat)

            if sam:
                sam = db.add_sample(sam,
                                    project=proj,
                                    material=mat,
                                    )

            dbln = db.get_labnumber(ln)
            if dbln:
                pos = dbln.irradiation_position
                lev = pos.level
                irrad = lev.irradiation
                if self.irradiation != irrad.name:
                    self.warning_dialog('Labnumber {} already exists in Irradiation {}'.format(ln, irrad.name))
                    return

                dbln.sample = db.get_sample(sam)

            else:
                dbln = db.add_labnumber(ln, sample=sam,)
                pos = db.add_irradiation_position(irs.hole, dbln, self.irradiation, self.level)

            def add_flux():
                hist = db.add_flux_history(pos)
                dbln.selected_flux_history = hist
                f = db.add_flux(irs.j, irs.j_err)
                f.history = hist

            if dbln.selected_flux_history:
                tol = 1e-10
                flux = dbln.selected_flux_history.flux
                if abs(flux.j - irs.j) > tol or abs(flux.j_err - irs.j_err) > tol:
                    add_flux()
            else:
                add_flux()

            db.commit()
#===============================================================================
# handlers
#===============================================================================
    def _add_irradiation_button_fired(self):
        irrad = Irradiation(db=self.db,
                            trays=self.trays
                            )
        info = irrad.edit_traits(kind='livemodal')
        if info.result:
            self._add_irradiation(irrad)
            self.irradiation = irrad.name
            self.saved = True

    def _add_irradiation(self, irrad):
        db = self.db
        ir = db.get_irradiation(irrad.name)
        if ir is not None:
            self.warning_dialog('Irradiation already exists')
            return
        else:
            prn = irrad.pr_name
            if not prn:
                prn = irrad.production_ratio_input.names[0]

            def make_ci(ci):
                return '{} {}%{} {}'.format(ci.startdate, ci.starttime,
                                        ci.enddate, ci.endtime)
            err = irrad.chronology_input.validate_chronology()
#            if err :
#                self.warning_dialog('Invalid Chronology. {}'.format(err))
#                return

            chronblob = '$'.join([make_ci(ci) for ci in irrad.chronology_input.dosages])
            cr = db.add_irradiation_chronology(chronblob)

            ir = db.add_irradiation(irrad.name, prn, cr)

#            holder = db.get_irradiation_holder(self.holder)
#            alpha = [chr(i) for i in range(65, 65 + self.ntrays)]
#            for ni in alpha:
#                db.add_irradiation_level(ni, ir, holder)

            db.commit()


    def _add_level_button_fired(self):
        irrad = self.irradiation
        irrad = self.db.get_irradiation(irrad)
        try:
            lastlevel = irrad.levels[-1].name
            nind = ALPHAS.index(lastlevel) + 1
        except IndexError:
            nind = 0

        try:
            t = Level(name=ALPHAS[nind],
                      tray=self.tray_name,
                      trays=self.trays)
        except IndexError:
            self.warning_dialog('Too many Trays')
            return

        info = t.edit_traits(kind='livemodal')
        if info.result:
            irrad = self.db.get_irradiation(irrad)
            if not next((li for li in irrad.levels if li.name == t.name), None):
                self.db.add_irradiation_level(t.name, irrad, t.tray)
                self.db.commit()
                self.level = t.name
                self.saved = True
            else:
                self.warning_dialog('Level {} already exists for Irradiation {}'.format(self.irradiation))

    def _save_button_fired(self):
        self._save_to_db()

    def _freeze_button_fired(self):
        for si in self.selected:
            si.auto_assigned = False

    def _thaw_button_fired(self):
        for si in self.selected:
            si.auto_assigned = True


    @on_trait_change('auto+')
    def _auto_update(self, obj, name, old, new):
        cnt = 0
#        print name, old, new
        if self.auto_assign:
            for s in self.irradiated_samples:
                rid = str(self.auto_startrid + cnt)
                if s.labnumber:
                    if self.auto_assign_overwrite or s.auto_assigned:
                        self._set_auto_params(s, rid)
                        s.auto_assigned = True
                        cnt += 1
                else:
                    self._set_auto_params(s, rid)
                    s.auto_assigned = True
                    cnt += 1


#                if self.auto_assign:
#                if s.labnumber:
#                    if self.auto_assign_overwrite or name != 'auto_assign':
#                        self._set_auto_params(s, rid)
#                        cnt += 1
#                else:
#                    self._set_auto_params(s, rid)
#                    cnt += 1

        self._update_sample_table = True

    @on_trait_change('level, irradiation')
    def irrad_change(self, obj, name, old, new):
        irrad = self.db.get_irradiation(self.irradiation)
        level = next((li for li in irrad.levels if li.name == self.level), None)
        if level:

            holder = level.holder.name
            if holder:
                self._load_irradiated_samples(holder)

            positions = level.positions
            if positions:
                for pi in positions:
                    ir = self._position_factory(pi)
                    hi = pi.position - 1
                    self.irradiated_samples[hi] = ir

    def _position_factory(self, dbpos):
        ln = dbpos.labnumber
        position = int(dbpos.position)

#        sample = None
#        material = None
#        project = None
        labnumber = ln.labnumber if ln else None
        ir = IrradiatedSample(labnumber=str(labnumber), hole=position)
        if labnumber:
            selhist = ln.selected_flux_history
            if selhist:
                flux = selhist.flux
                if flux:
                    ir.j = flux.j
                    ir.j_err = flux.j_err
#            p = next((pi for pi in ln.irradiation.positions if pi.position == position), None)
#            if p:
#                p.flux
#                
            sample = ln.sample
            if sample:
                ir.sample = sample.name
                material = sample.material
                project = sample.project
                if project:
                    ir.project = project.name
#                    project = project.name
                if material:
                    ir.material = material.name
#                    material = material.name


#        ir = IrradiatedSample(labnumber=str(labnumber),
#                              sample=sample if sample else '',
#                              material=material if material else '',
#                              project=project if project else '',
#                              hole=position)
        return ir

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_irradiations(self):
#        r = ['NM-Test', 'NM-100', 'NM-200']
        r = [str(ri.name) for ri in self.db.get_irradiations() if ri.name]
        if r and not self.irradiation:
            self.irradiation = r[-1]
        return r

    def _get_levels(self):
        r = []
        irrad = self.db.get_irradiation(self.irradiation)
        if irrad:
            r = [str(ri.name) for ri in irrad.levels]
            if r and not self.level:
                self.level = r[-1]
        return r

    def _get_irradiation_tray_image(self):
        p = self._get_map_path()
#        ir = self.db.get_irradiation(self.irradiation)

        level = self.db.get_irradiation_level(self.irradiation, self.level)
        holder = None
        if level:
            holder = level.holder
            holder = holder.name if holder else None
        holder = holder if holder is not None else '---'
        self.tray_name = holder
        im = ImageResource('{}.png'.format(holder),
                             search_path=[p]
                             )
        return im

    @cached_property
    def _get_trays(self):

        p = self._get_map_path()
        if not os.path.isdir(p):
            self.warning_dialog('{} does not exist'.format(p))
            return Undefined

        ts = [pi for pi in os.listdir(p)
                    if not (pi.endswith('.png')
                            or pi.endswith('.pct')
                            or pi.startswith('.'))]
        if ts:
            self.tray = ts[-1]

        return ts
    def _get_map_path(self):
        return os.path.join(paths.setup_dir, 'irradiation_tray_maps')

    def traits_view(self):
        irradiation = Group(
                            HGroup(
                                   VGroup(Item('irradiation',
                                               editor=EnumEditor(name='irradiations')
                                               ),
                                        Item('level',
                                             editor=EnumEditor(name='levels')
                                             ),
                                          Item('add_irradiation_button', show_label=False),
                                          Item('add_level_button', show_label=False),
#                                        Item('irradiation_tray',
#                                             editor=EnumEditor(name='irradiation_trays')
#                                             )
                                          ),
                                   spring,
                                   VGroup(
                                          Item('tray_name', style='readonly', show_label=False),
                                          Item('irradiation_tray_image',
                                               editor=ImageEditor(),
                                               height=200,
                                               width=200,
                                               style='custom',
                                               show_label=False),
                                          ),
                                        ),
                            label='Irradiation',
                            show_border=True
                            )

        auto = Group(
                    Item('auto_assign', label='Auto-assign Labnumbers'),
                    Item('auto_startrid', label='Start Labnumber',
                         enabled_when='auto_assign'
                         ),
                    Item('auto_project', label='Project',
                         enabled_when='auto_assign'
                         ),
                    Item('auto_sample', label='Sample',
                         enabled_when='auto_assign'
                         ),
                    Item('auto_material', label='Material',
                         enabled_when='auto_assign'
                         ),
                     Item('auto_j', format_str='%0.2e', label='Nominal J.'),
                     Item('auto_j_err', format_str='%0.2e', label='Nominal J Err.'),
                    Item('auto_assign_overwrite', label='Overwrite exisiting Labnumbers',
                         enabled_when='auto_assign'
                         ),
                      HGroup(Item('freeze_button', show_label=False), Item('thaw_button', show_label=False),
                              enabled_when='selected'),
                      show_border=True,
                      label='Auto-Assign'

                      )

        samples = Group(

                        Item('irradiated_samples',
                             editor=TabularEditor(adapter=IrradiatedSampleAdapter(),
                                                  update='_update_sample_table',
                                                  multi_select=True,
                                                  selected='selected',
                                                  operations=['edit']
                                                  ),
                             show_label=False
                             ),
                        label='Lab Numbers',
                        show_border=True
                        )
        v = View(VGroup(
                        HGroup(auto, irradiation),
                        samples,
                        HGroup(spring, Item('save_button', show_label=False))
                        ),
                 resizable=True,
                 width=900,
                 height=600,
                 )
        return v
if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    paths.build('_test')

    logging_setup('runid')
    m = LabnumberEntry()
    m.configure_traits()
#============= EOF =============================================
