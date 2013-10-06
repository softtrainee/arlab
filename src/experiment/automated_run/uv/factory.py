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
from traits.api import Str, Property, Int, List, Button, \
     cached_property
from traitsui.api import Item, EnumEditor, HGroup, VGroup, Group
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.experiment.automated_run.factory import AutomatedRunFactory
from src.constants import NULL_STR
from src.experiment.automated_run.uv.factory_view import UVFactoryView
from src.experiment.automated_run.uv.spec import UVAutomatedRunSpec
from src.paths import paths


class UVAutomatedRunFactory(AutomatedRunFactory):
    reprate = Int
    mask = Str
    attenuator = Str
    image = Str

    masks = Property
    extract_units_names = List([NULL_STR, 'burst', 'continuous'])
    _default_extract_units = 'burst'
    browser_button = Button('Browse')

    _spec_klass = UVAutomatedRunSpec
    factory_view_klass = UVFactoryView

    @cached_property
    def _get_masks(self):
        p = os.path.join(paths.device_dir, 'uv', 'masks.txt')
        masks = []
        if os.path.isfile(p):
            with open(p, 'r') as fp:
                for lin in fp:
                    lin = lin.strip()
                    if not lin or lin.startswith('#'):
                        continue
                    masks.append(lin)

        return masks
    def _get_supplemental_extract_group(self):
        g = VGroup(Item('reprate'),
                   Item('mask', editor=EnumEditor(name='masks')),
                   Item('attenuator'),
                   HGroup(Item('image', springy=True), Item('browser_button', show_label=False)),
                   label='UV'
                   )
        return g

    def _get_extract_group(self):
        sgrp = self._get_supplemental_extract_group()
        grp = super(UVAutomatedRunFactory, self)._get_extract_group()
        grp.show_border = False
#        grp.label = ''

        ngrp = Group(
                     grp,
                     sgrp,
                     layout='tabbed')

        return ngrp


#============= EOF =============================================
