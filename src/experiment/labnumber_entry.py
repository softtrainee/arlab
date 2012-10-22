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
    List, on_trait_change, Int, Bool, Event, Any, Button
from traitsui.api import View, Item, EnumEditor, \
     VGroup, HGroup, Spring, spring, Group, Image, ImageEditor, TabularEditor, \
     Handler

from traitsui.tabular_adapter import TabularAdapter
from pyface.image_resource import ImageResource

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.loggable import Loggable
from src.paths import paths


class IrradiatedSample(HasTraits):
    labnumber = Str
    material = Str
    sample = Str
    hole = Int
    project = Str
    size = Str
    weight = Str
    note = Str


class IrradiatedSampleAdapter(TabularAdapter):
    columns = [
               ('Location', 'hole'),
               ('Labnumber', 'labnumber'),
               ('Sample', 'sample'),
               ('Project', 'project'),
               ('Material', 'material'),
               ('Size', 'size'),
               ('Weight', 'weight'),
               ('Note', 'note')
             ]
    hole_can_edit = False
    hole_width = Property
    def _get_hole_width(self):
        return 35


class LabnumberEntry(Loggable):
    db = Any
    irradiation = Str
    sub_irradiation = Str
    irradiation_tray = Str

    irradiations = Property
    sub_irradiations = Property(depends_on='irradiations')
    irradiation_trays = Property
    irradiation_tray_image = Property(Image, depends_on='irradiation_tray')

    irradiated_samples = List(IrradiatedSample)

    auto_assign = Bool
    auto_startrid = Int(19999)
    auto_assign_overwrite = Bool(False)
    auto_project = Str('Foo')
    auto_sample = Str('FC-2')
    auto_material = Str('sanidine')

    _update_sample_table = Event

    save_button = Button('Save')

    def _set_auto_params(self, s, rid):
        s.labnumber = rid
        s.sample = self.auto_sample
        s.project = self.auto_project
        s.material = self.auto_material

    def _load_irradiated_samples(self, name):
        p = os.path.join(self._get_map_path(), name)
        self.irradiated_samples = []
        with open(p, 'r') as f:
            line = f.readline()
            nholes, diam = line.split(',')
            for ni in range(int(nholes)):
                self.irradiated_samples.append(IrradiatedSample(hole=ni + 1))

    def _save_to_db(self):
        db = self.db
        for irs in self.irradiated_samples:
            ln = irs.labnumber
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

            db.add_labnumber(ln, sample=sam,
                                    commit=True)

        db.commit()
#===============================================================================
# handlers
#===============================================================================
    def _save_button_fired(self):
        self._save_to_db()

    @on_trait_change('auto+')
    def _auto_update(self, obj, name, old, new):
        cnt = 0
        for s in self.irradiated_samples:
            rid = str(self.auto_startrid + cnt)
            if self.auto_assign:
                if s.labnumber:
                    if self.auto_assign_overwrite or name != 'auto_assign':
                        self._set_auto_params(s, rid)
                else:
                    self._set_auto_params(s, rid)

            cnt += 1

        self._update_sample_table = True

    @on_trait_change('irradiation_tray')
    def irrad_change(self, obj, name, old, new):
        self._load_irradiated_samples(new)
#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_irradiations(self):
        r = ['NM-Test', 'NM-100', 'NM-200']
        if r:
            self.irradiation = r[-1]
        return r

    def _get_sub_irradiations(self):
        r = ['A', 'B']
        if r:
            self.sub_irradiation = r[-1]
        return r

    @cached_property
    def _get_irradiation_trays(self):

        p = self._get_map_path()
        ts = [pi for pi in os.listdir(p)
                    if not (pi.endswith('.png')
                            or pi.endswith('.pct')
                            or pi.startswith('.'))]
        if ts:
            self.irradiation_tray = ts[-1]

        return ts

    def _get_irradiation_tray_image(self):
        p = self._get_map_path()
        im = ImageResource('{}.png'.format(self.irradiation_tray),
                             search_path=[p]
                             )
        return im

    def _get_map_path(self):
        return os.path.join(paths.setup_dir, 'irradiation_tray_maps')

    def traits_view(self):
        irradiation = Group(
                            HGroup(
                                   VGroup(Item('irradiation',
                                               editor=EnumEditor(name='irradiations')
                                               ),
                                        Item('sub_irradiation',
                                             editor=EnumEditor(name='sub_irradiations')
                                             ),
                                        Item('irradiation_tray',
                                             editor=EnumEditor(name='irradiation_trays')
                                             )),
                                    Item('irradiation_tray_image',
                                         editor=ImageEditor(),
                                         height=150,
                                          style='custom',
                                          show_label=False),
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

                    Item('auto_assign_overwrite', label='Overwrite exisiting Labnumbers',
                         enabled_when='auto_assign'
                         ),
                      show_border=True,
                      label='Auto-Assign'
                      )

        samples = Group(

                        Item('irradiated_samples',
                             editor=TabularEditor(adapter=IrradiatedSampleAdapter(),
                                                  update='_update_sample_table',
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
