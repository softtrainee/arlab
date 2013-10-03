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
# from src.processing.entry.flux_monitor import FluxMonitor
# from src.processing.entry.db_entry import DBEntry
# from src.irradiation.irradiated_position import IrradiatedPosition, \
#    IrradiatedPositionAdapter
from src.constants import NULL_STR, ALPHAS
from src.database.isotope_database_manager import IsotopeDatabaseManager
from src.processing.entry.irradiated_position import IrradiatedPosition
# import math
# from src.processing.publisher.writers.pdf_writer import SimplePDFWriter
# from src.processing.publisher.templates.tables.irradiation_table import IrradiationTable
# from src.database.orms.isotope_orm import gen_ProjectTable, gen_SampleTable
from src.database.orms.isotope.gen import gen_ProjectTable, gen_SampleTable
from src.codetools.simple_timeit import timethis, simple_timer
# from src.ui.thread import Thread
# from pyface.timer.do_later import do_later
import struct




class LabnumberEntry(IsotopeDatabaseManager):

    irradiation_tray = Str
    trays = Property

    edit_irradiation_button = Button('Edit')
    edit_level_enabled = Property(depends_on='level')
    edit_irradiation_enabled = Property(depends_on='irradiation')

    tray_name = Str
    irradiation_tray_image = Property(Image, depends_on='level, irradiation, saved')
    irradiated_positions = List(IrradiatedPosition)

    add_irradiation_button = Button('Add Irradiation')
    add_level_button = Button('Add Level')
    edit_level_button = Button('Edit')
    load_file_button = Button('Load File')
    generate_labnumbers_button = Button('Generate Labnumbers')
    #===========================================================================
    # irradiation positions table events
    #===========================================================================
    selected = Any
    refresh_table = Event

    #===========================================================================
    # factory traits
    #===========================================================================
    sample = Str
    samples = Property
    add_sample_button = Button('+')

    material = Str
    materials = Property
    add_material_button = Button('+')

    project = Str
    projects = Property
    add_project_button = Button('+')


    #===========================================================================
    #
    #===========================================================================

    def __init__(self, *args, **kw):
        super(LabnumberEntry, self).__init__(*args, **kw)
        self.populate_default_tables()

    def make_table(self):
        from src.processing.publisher.writers.pdf_writer import SimplePDFWriter
        from src.processing.publisher.templates.tables.irradiation_table import IrradiationTable

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

    def finalize_irradiation(self, dry_run=False):
        '''
            generate labnumbers
            
            lock irradiation table
            
            make pdf table
        '''
        db = self.db
        irrad = db.get_irradiation(self.irradiation)

        offset = 0
        level_offset = 0
        self._generate_labnumbers(offset, level_offset, dry_run)

        irrad.locked = True
        if not dry_run:
            db.commit()

    def _generate_labnumbers(self, offset=0, level_offset=0, dry_run=False):
        '''
            get last labnumber 
            
            start numbering at add 1+offset
            
            add level_offset between each level
        '''
        ir = self.irradiation
        lngen = self._labnumber_generator(ir,
                                          offset,
                                          level_offset
                                          )
        db = self.db
        while 1:
            try:
                pos, ln = lngen.next()
            except StopIteration:
                break

            pos.labnumber.identifier = ln
            le = pos.level.name
            pi = pos.position
            self.info('setting irrad. pos. {} {}-{} labnumber={}'.format(ir, le, pi, ln))

        if not dry_run:
            db.commit()

        self._update_level()

    def _labnumber_generator(self, irradiation, offset, level_offset):

        def gen(offset, level_offset):
            db = self.db
            last_ln = db.get_last_labnumber()
            if last_ln:
                last_ln = int(last_ln.identifier)
            else:
                last_ln = 0

            i = 0
            if not offset:
                last_ln += 1

            sln = last_ln + offset
            irrad = db.get_irradiation(irradiation)

#             for _ in range(3):
#                 for _ in range(2):
            for level in irrad.levels:
                for position in level.positions:
                    yield position, sln + i
                    i += 1

                if level_offset:
                    sln = sln + level_offset
                    i = 0
                    if not offset:
                        i = -1


        return gen(offset, level_offset)

    def _load_positions_from_file(self, p, dry_run=False):
        '''
            use an xls file to enter irradiation positions
            
            sheet must be named IrradiationInfo or the first sheet
            
            add level
            
            add project
            add sample
            add material
            
            optional:
                weight
            
            add irradiation_position
            add labnumber.  since sample info is associated with labnumber table
            need to add a labnumber entry now. dont set the identifier yet tho
            
            commit to database
            
            load positions from database into table for viewing
            
        '''
        from src.managers.data_managers.xls_data_manager import XLSDataManager

        db = self.db
        irradiation = self.irradiation

        dm = XLSDataManager()
        dm.open(p)

        header_offset = 1
        sheet = dm.get_sheet(('IrradiationInfo', 0))

        project_idx = dm.get_column_idx('project', sheet=sheet)
        sample_idx = dm.get_column_idx('sample', sheet=sheet)
        material_idx = dm.get_column_idx('material', sheet=sheet)
        level_idx = dm.get_column_idx('level', sheet=sheet)
        holder_idx = dm.get_column_idx('holder', sheet=sheet)
        pos_idx = dm.get_column_idx('position', sheet=sheet)
        weight_idx = dm.get_column_idx('weight', sheet=sheet)

        for ri in range(sheet.nrows - header_offset):
            ri += header_offset
            level = sheet.cell_value(ri, level_idx)
            holder = sheet.cell_value(ri, holder_idx)

            dblevel = db.add_irradiation_level(level, irradiation, holder)

            project = sheet.cell_value(ri, project_idx)
            material = sheet.cell_value(ri, material_idx)
            sample = sheet.cell_value(ri, sample_idx)

            prj = db.add_project(project)
            mat = db.add_material(material)
            db.add_sample(sample, project=prj, material=mat)

            pos = sheet.cell_value(ri, pos_idx)

            dbln = db.add_labnumber('', sample=sample,
                                        unique=False)

            weight = None
            if weight_idx:
                weight = sheet.cell_value(ri, weight_idx)
            db.add_irradiation_position(pos, dbln, irradiation, dblevel,
                                        weight=weight,
                                        )

        if not dry_run:
            db.commit()

        self.updated = True
        self.level = level
#         self._update_level()

    # @simple_timer()
    def _load_holder_positions(self, holder):
        self.irradiated_positions = []
        geom = holder.geometry
        if geom:
            self.irradiated_positions = [IrradiatedPosition(hole=c + 1,
                                                            pos=struct.unpack('>ff',
                                                                              geom[i:i + 8]))
                                        for c, i in enumerate(xrange(0, len(geom), 8))]


        elif holder.name:
            self._load_holder_positons_from_file(holder.name)

    def _load_holder_positons_from_file(self, name):
            p = os.path.join(self._get_map_path(), name)
            self.irradiated_positions = []
            with open(p, 'r') as f:
                line = f.readline()
                nholes, _diam = line.split(',')
                self.irradiated_positions = [IrradiatedPosition(hole=ni + 1)
                                             for ni in range(int(nholes))
                                             ]

#                 for ni in range(int(nholes)):
#                     self.irradiated_positions.append(IrradiatedPosition(hole=ni + 1))

    def _save_to_db(self):
        db = self.db
        with db.session_ctx():
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
                    if pos is None:
                        pos = db.add_irradiation_position(irs.hole, dbln, self.irradiation, self.level)
                    else:
                        lev = pos.level
                        irrad = lev.irradiation
                        if self.irradiation != irrad.name:
                            self.warning_dialog('Labnumber {} already exists in Irradiation {}'.format(ln, irrad.name))
                            return
                        if irs.hole!=pos.position:
                            pos=db.add_irradiation_position(irs.hole, dbln, self.irradiation, self.level)

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

                self.info('changes saved to database')

#===============================================================================
# handlers
#===============================================================================
    def _generate_labnumbers_button_fired(self):
        self._generate_labnumbers(offset=0,
                                  level_offset=0,
                                  dry_run=False)

    def _load_file_button_fired(self):
        p = self.open_file_dialog()
        if p:
            self._load_positions_from_file(p)

    def _add_irradiation_button_fired(self):
        irrad = Irradiation(db=self.db,
                            trays=self.trays
                            )


        while 1:
            info = irrad.edit_traits(kind='livemodal')
            if info.result:
                result = irrad.save_to_db()
                if result is True:
                    self.irradiation = irrad.name
                    self.saved = True

                    break
                elif result is False:
                    break
            else:
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


#         self.irradiated_positions = []


#     _level_thread = None
    def _level_changed(self):
#         if self._level_thread:
#             if self._level_thread.isRunning():
#                 return
        self.debug('level changed')
        self.irradiated_positions = []
        if self.level:
            self._update_level()

#         from threading import Thread
#         t = Thread(target=self._update_level)
#         t.start()
#         self._level_thread = t
#         t.join()

    # @simple_timer()
    def _update_level(self, name=None):

        if name is None:
            name = self.level

        db = self.db
        with db.session_ctx():
            level = db.get_irradiation_level(self.irradiation, name)

            if not level:
                self.debug('no level for {}'.format(name))
                return

            self.debug('holder {}'.format(level.holder))
            if level.holder:
                self._load_holder_positions(level.holder)

            positions = level.positions
            n = len(self.irradiated_positions)
            self.debug('positions in level {}.  \
                        available holder positions{}'.format(n, len(self.irradiated_positions)))
            if positions:
                self._make_positions(n, positions)

    # @simple_timer()
    def _make_positions(self, n, positions):
        for pi in positions:
            hi = pi.position - 1
            if hi < n:
                ir = self.irradiated_positions[hi]
                self._position_factory(pi, ir)
            else:
                self.debug('extra irradiation position for this tray {}'.format(hi))


    @on_trait_change('project, sample')
    def _edit_handler(self, name, new):
        if self.selected:

            for si in self.selected:
                setattr(si, name, new)

            if name == 'sample':
                sample = self.db.get_sample(new)
                material = sample.material
                material = material.name if material else ''

                for si in self.selected:
                    setattr(si, 'material', material)


        self.refresh_table = True

#===============================================================================
# factorys
#===============================================================================
    def _position_factory(self, dbpos, ir):
        ln = dbpos.labnumber
        position = int(dbpos.position)

        labnumber = ln.identifier if ln else None
        ir.trait_set(labnumber=str(labnumber), hole=position)
#         ir = IrradiatedPosition(labnumber=str(labnumber), hole=position)
#         if labnumber:
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

        if dbpos.weight:
            ir.weight = str(dbpos.weight)

        note = ln.note
        if note:
            ir.note = note

        return ir

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_projects(self):
        order = gen_ProjectTable.name.asc()
        projects = [''] + [pi.name for pi in self.db.get_projects(order=order)]
        return projects

    @cached_property
    def _get_samples(self):
        order = gen_SampleTable.name.asc()
        samples = [''] + [si.name for si in self.db.get_samples(order=order)]
        return samples

    @cached_property
    def _get_materials(self):
        materials = [''] + [mi.name for mi in self.db.get_materials()]
        return materials

    def _get_irradiation_tray_image(self):
        p = self._get_map_path()
        db = self.db
        with db.session_ctx():
            level = db.get_irradiation_level(self.irradiation,
                                             self.level)
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
#     def _set_auto_params(self, s, rid):
#         s.labnumber = rid
#         s.sample = self.auto_sample
#         s.project = self.auto_project
#         s.material = self.auto_material
#         s.j = self.auto_j
#         s.j_err = self.auto_j_err
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
#     auto_assign = Bool
#     auto_startrid = Int(19999)
#     auto_assign_overwrite = Bool(False)
#     auto_project = Str('Foo')
#     auto_sample = Str('FC-2')
#     auto_material = Str('sanidine')
#     auto_j = Float(1e-4)
#     auto_j_err = Float(1e-7)
#     freeze_button = Button('Freeze')
#     thaw_button = Button('Thaw')

#     _update_sample_table = Event

#    save_button = Button('Save')

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
