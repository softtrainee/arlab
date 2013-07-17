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
from traits.api import  Property, Str, cached_property, \
    List, on_trait_change, Int, Bool, Event, Any, Button, Undefined, Float
from traitsui.api import View, Item, EnumEditor, \
     VGroup, HGroup, spring, Group, Image, ImageEditor, TabularEditor
from pyface.image_resource import ImageResource

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.paths import paths
from src.processing.entry.irradiation import Irradiation
from src.processing.entry.level import Level
from src.processing.entry.flux_monitor import FluxMonitor
from src.processing.entry.db_entry import DBEntry
# from src.irradiation.irradiated_position import IrradiatedPosition, \
#    IrradiatedPositionAdapter
from src.constants import NULL_STR, ALPHAS
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.processing.entry.irradiated_position import IrradiatedPositionAdapter, \
    IrradiatedPosition
import math
from src.processing.publisher.writers.pdf_writer import SimplePDFWriter
from src.processing.publisher.templates.tables.irradiation_table import IrradiationTable


class LabnumberEntry(IsotopeDatabaseManager):

#    irradiation = Str
#    level = Str
    irradiation_tray = Str

#    irradiations = Property(depends_on='saved, updated')
#    levels = Property(depends_on='irradiation,saved, updated')
    trays = Property
    edit_irradiation_button = Button('Edit')
    edit_level_enabled = Property(depends_on='level')
    edit_irradiation_enabled = Property(depends_on='irradiation')
#    saved = Event
#    updated = Event
#    irradiation_trays = Property
    tray_name = Str
    irradiation_tray_image = Property(Image, depends_on='level, irradiation, saved')
    irradiated_positions = List(IrradiatedPosition)

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

#    save_button = Button('Save')
    add_irradiation_button = Button('Add Irradiation')
    add_level_button = Button('Add Level')
    edit_level_button = Button('Edit')

    selected = Any

    def __init__(self, *args, **kw):
        super(LabnumberEntry, self).__init__(*args, **kw)
        self.populate_default_tables()

    def make_table(self):
        out = '/Users/ross/Sandbox/irradiation.pdf'
        w = SimplePDFWriter(filename=out)

        irrad = self.db.get_irradiation(self.irradiation)

        def make_row(pos):
            ln = pos.labnumber
            sample = ''
            identifier = ''
            if ln:
                if ln.sample:
                    sample = ln.sample.name
                identifier = ln.identifier

            return [pos.position, identifier, sample]

        for level in irrad.levels:

            t = IrradiationTable()
            rows = sorted([make_row(pi) for pi in level.positions],
                          key=lambda x:x[0]
                          )
            rows = [
                    [self.irradiation, level.name, ''],
                    ['Pos.', 'L#', 'Sample'],
                    ] + rows


            ta = t.make(rows)
            w.add(ta)
        w.publish(use_landscape=False)


    def save(self):
        self._save_to_db()

    def populate_default_tables(self):
        db = self.db
        if self.db:
            if db.connect():

                from src.database.defaults import load_isotopedb_defaults
                load_isotopedb_defaults(db)

    def _set_auto_params(self, s, rid):
        s.labnumber = rid
        s.sample = self.auto_sample
        s.project = self.auto_project
        s.material = self.auto_material
        s.j = self.auto_j
        s.j_err = self.auto_j_err

    def _load_holder_positions(self, holder):
        self.irradiated_positions = []
        import struct
        geom = holder.geometry
        if geom:
            geom = [struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)]
#             offset = 0
            i = 1
            c = 1
#             pr = 1
            for x, y in geom:
#                 '''
#                     assume points listed in clockwise order
#
#                     increment hole_offset when passed 12 oclock
#
#                 '''
#                 r = math.atan2(x, y)
#                 if pr < 0 and r >= 0:
#                     offset = 100 * i
#                     i += 1
#                     c = 0
#                 pr = r

                self.irradiated_positions.append(IrradiatedPosition(
                                                                    hole=c,
#                                                                     alt_hole=c + offset,
                                                                    x=x, y=y
                                                                    ))
                c += 1

        elif holder.name:
            self._load_holder_positons_from_file(holder.name)

    def _load_holder_positons_from_file(self, name):
            p = os.path.join(self._get_map_path(), name)
            self.irradiated_positions = []
            with open(p, 'r') as f:
                line = f.readline()
                nholes, diam = line.split(',')
                for ni in range(int(nholes)):
                    self.irradiated_positions.append(IrradiatedPosition(hole=ni + 1))

    def _save_to_db(self):
        db = self.db

        for irs in self.irradiated_positions:
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
                dbln.note = irs.note

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

            self.info('changes saved to database')

#===============================================================================
# handlers
#===============================================================================
    def _add_irradiation_button_fired(self):
        irrad = Irradiation(db=self.db,
                            trays=self.trays
                            )
        while 1:
            info = irrad.edit_traits(kind='livemodal')
            if info.result:
                if irrad.save_to_db():
    #            self._add_irradiation(irrad)
                    self.irradiation = irrad.name
                    self.saved = True
                    break

    def _edit_irradiation_button_fired(self):
        irrad = Irradiation(db=self.db,
                            trays=self.trays,
                            name=self.irradiation
                            )
        irrad.load_production_name()
        irrad.load_chronology()

        info = irrad.edit_traits(kind='livemodal')
        if info.result:
            irrad.edit_db()

    def _edit_level_button_fired(self):

        _prev_tray = self.tray_name
        irradiation = self.irradiation
        level = Level(db=self.db,
                      name=self.level,
                      trays=self.trays
                      )
        level.load(irradiation)
        info = level.edit_traits(kind='livemodal')
        if info.result:

            self.info('saving level. Irradiation={}, Name={}, Tray={}, Z={}'.format(irradiation,
                                                                                    level.name,
                                                                                    level.tray,
                                                                                    level.z))
            level.edit_db()

            self.saved = True
            self.irradiation = irradiation
            self.level = level.name

            if _prev_tray != level.tray:
                if not self.confirmation_dialog('Irradiation Tray changed. Copy labnumbers to new tray'):
                    self._load_holder_positions(level.tray)


    def _add_level_button_fired(self):
        irrad = self.irradiation
        irrad = self.db.get_irradiation(irrad)
        try:
            level = irrad.levels[-1]
            lastlevel = level.name
            lastz = level.z
            nind = list(ALPHAS).index(lastlevel) + 1
        except IndexError:
            nind = 0
            lastz = 0

        try:
            t = Level(name=ALPHAS[nind],
                      z=lastz if lastz is not None else 0,
                      tray=self.tray_name,
                      trays=self.trays)
        except IndexError:
            self.warning_dialog('Too many Trays')
            return

        info = t.edit_traits(kind='livemodal')
        if info.result:
            irrad = self.db.get_irradiation(irrad)
            if not next((li for li in irrad.levels if li.name == t.name), None):
                self.db.add_irradiation_level(t.name, irrad, t.tray, t.z)
                self.db.commit()
                self.level = t.name
                self.saved = True
            else:
                self.warning_dialog('Level {} already exists for Irradiation {}'.format(self.irradiation))

#    def _save_button_fired(self):
#        self._save_to_db()

#     def _freeze_button_fired(self):
#         for si in self.selected:
#             si.auto_assigned = False
#
#     def _thaw_button_fired(self):
#         for si in self.selected:
#             si.auto_assigned = True
#
#
#     @on_trait_change('auto+')
#     def _auto_update(self, obj, name, old, new):
#         cnt = 0
# #        print name, old, new
#         if self.auto_assign:
#             for s in self.irradiated_positions:
#                 rid = str(self.auto_startrid + cnt)
#                 if s.labnumber:
#                     if self.auto_assign_overwrite or s.auto_assigned:
#                         self._set_auto_params(s, rid)
#                         s.auto_assigned = True
#                         cnt += 1
#                 else:
#                     self._set_auto_params(s, rid)
#                     s.auto_assigned = True
#                     cnt += 1
#
#
# #                if self.auto_assign:
# #                if s.labnumber:
# #                    if self.auto_assign_overwrite or name != 'auto_assign':
# #                        self._set_auto_params(s, rid)
# #                        cnt += 1
# #                else:
# #                    self._set_auto_params(s, rid)
# #                    cnt += 1
#
#         self._update_sample_table = True

    def _level_changed(self):
        self.irradiated_positions = []

        irrad = self.db.get_irradiation(self.irradiation)
        if not irrad:
            return

        level = next((li for li in irrad.levels if li.name == self.level), None)
        if level:
            if level.holder:
                self._load_holder_positions(level.holder)

            positions = level.positions
            if positions:
                for pi in positions:
                    ir = self._position_factory(pi)
                    hi = pi.position - 1
                    self.irradiated_positions[hi] = ir

    def _position_factory(self, dbpos):
        ln = dbpos.labnumber
        position = int(dbpos.position)

        labnumber = ln.identifier if ln else None
        ir = IrradiatedPosition(labnumber=str(labnumber), hole=position)
        if labnumber:
            selhist = ln.selected_flux_history
            if selhist:
                flux = selhist.flux
                if flux:
                    ir.j = flux.j
                    ir.j_err = flux.j_err
#
            sample = ln.sample
            if sample:
                ir.sample = sample.name
                material = sample.material
                project = sample.project
                if project:
                    ir.project = project.name
                if material:
                    ir.material = material.name
            note = ln.note
            if note:
                ir.note = note

        return ir

#===============================================================================
# property get/set
#===============================================================================

    def _get_irradiation_tray_image(self):
        p = self._get_map_path()
#        ir = self.db.get_irradiation(self.irradiation)

        level = self.db.get_irradiation_level(self.irradiation, self.level)
        holder = None
        if level:
            holder = level.holder
            holder = holder.name if holder else None
        holder = holder if holder is not None else NULL_STR
        self.tray_name = holder
        im = ImageResource('{}.png'.format(holder),
                             search_path=[p]
                             )
        return im

    @cached_property
    def _get_flux_monitors(self):
        db = self.db
        fs = db.get_flux_monitors()
        if fs:
            fs = [fi.name for fi in db.get_flux_monitors()]
        else:
            fs = []
        return fs

    @cached_property
    def _get_trays(self):

        p = os.path.join(self._get_map_path(), 'images')
        if not os.path.isdir(p):
            self.warning_dialog('{} does not exist'.format(p))
            return Undefined

        ts = [os.path.splitext(pi)[0] for pi in os.listdir(p) if not pi.startswith('.')
#                    if not (pi.endswith('.png')
#                            or pi.endswith('.pct')
#                            or pi.startswith('.'))
              ]
        if ts:
            self.tray = ts[-1]

        return ts

    def _get_map_path(self):
        return os.path.join(paths.setup_dir, 'irradiation_tray_maps')

    def _get_calculate_flux_enabled(self):
        if self.selected:
            return len(self.selected) >= 3

    def _get_edit_irradiation_enabled(self):
        return self.irradiation is not None

    def _get_edit_level_enabled(self):
        return self.level is not None



if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    paths.build('_experiment')

    logging_setup('runid')
    m = LabnumberEntry()
    m.configure_traits()
#============= EOF =============================================
#     def traits_view(self):
#         irradiation = Group(
#                             HGroup(
#                                    VGroup(HGroup(Item('irradiation',
#                                                       editor=EnumEditor(name='irradiations')
#                                                       ),
#                                                  Item('edit_irradiation_button',
#                                                       enabled_when='edit_irradiation_enabled',
#                                                       show_label=False)
#                                                  ),
#                                           HGroup(Item('level', editor=EnumEditor(name='levels')),
#                                                  spring,
#                                                  Item('edit_level_button',
#                                                       enabled_when='edit_level_enabled',
#                                                       show_label=False)
#                                                  ),
#                                           Item('add_irradiation_button', show_label=False),
#                                           Item('add_level_button', show_label=False),
# #                                        Item('irradiation_tray',
# #                                             editor=EnumEditor(name='irradiation_trays')
# #                                             )
#                                           ),
#                                    spring,
#                                    VGroup(
#                                           Item('tray_name', style='readonly', show_label=False),
#                                           Item('irradiation_tray_image',
#                                                editor=ImageEditor(),
#                                                height=200,
#                                                width=200,
#                                                style='custom',
#                                                show_label=False),
#                                           ),
#                                         ),
#                             label='Irradiation',
#                             show_border=True
#                             )
#
#         auto = Group(
#                     Item('auto_assign', label='Auto-assign Labnumbers'),
#                     Item('auto_startrid', label='Start Labnumber',
#                          enabled_when='auto_assign'
#                          ),
#                     Item('auto_project', label='Project',
#                          enabled_when='auto_assign'
#                          ),
#                     Item('auto_sample', label='Sample',
#                          enabled_when='auto_assign'
#                          ),
#                     Item('auto_material', label='Material',
#                          enabled_when='auto_assign'
#                          ),
#                      Item('auto_j', format_str='%0.2e', label='Nominal J.'),
#                      Item('auto_j_err', format_str='%0.2e', label='Nominal J Err.'),
#                     Item('auto_assign_overwrite', label='Overwrite exisiting Labnumbers',
#                          enabled_when='auto_assign'
#                          ),
#                       HGroup(Item('freeze_button', show_label=False), Item('thaw_button', show_label=False),
#                               enabled_when='selected'),
#                       show_border=True,
#                       label='Auto-Assign'
#
#                       )
#
#         samples = Group(
#
#                         Item('irradiated_positions',
#                              editor=TabularEditor(adapter=IrradiatedPositionAdapter(),
#                                                   update='_update_sample_table',
#                                                   multi_select=True,
#                                                   selected='selected',
#                                                   operations=['edit']
#                                                   ),
#                              show_label=False
#                              ),
#                         label='Lab Numbers',
#                         show_border=True
#                         )
# #        flux = Group(
# #                     HGroup(
# #                            Item('flux_monitor', show_label=False, editor=EnumEditor(name='flux_monitors')),
# #                            Item('edit_monitor_button', show_label=False)),
# #                     Item('flux_monitor_age', format_str='%0.3f', style='readonly', label='Monitor Age (Ma)'),
# #                     Spring(height=50, springy=False),
# #                     Item('calculate_flux_button',
# #                          enabled_when='calculate_flux_enabled',
# #                          show_label=False),
# #                     label='Flux',
# #                     show_border=True
# #                     )
#         v = View(VGroup(
#                         HGroup(auto, irradiation,
# #                               flux
#                                ),
#                         samples,
#                         HGroup(spring, Item('save_button', show_label=False))
#                         ),
#                  resizable=True,
#                  width=0.75,
#                  height=600,
#                  title='Labnumber Entry'
#                  )
#         return v
