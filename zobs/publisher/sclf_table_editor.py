#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, File, Property, Button, Instance
from traitsui.api import View, Item, UItem, Image
from pyface.image_resource import ImageResource

#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.ui.image_editor import ImageEditor
import os

class TableTool(HasTraits):
    make_button = Button('Make')
    publish_button = Button('Publish')
    def traits_view(self):
        v = View(UItem('make_button',
                       tooltip='Construct a PNG draft of the table. Use Publish to make a PDF'),
                 UItem('publish_button',
                       tooltip='Save a PDF table'
                       )

                 )
        return v


class TableEditor(BaseTraitsEditor):
    table_image = Property(Image, depends_on='table_image_source')
    table_image_source = File
    name = Property(depends_on='table_image_source')
    tool = Instance(TableTool, ())
    def _get_name(self):
        if self.table_image_source:
            name = os.path.basename(self.table_image_source)
            name, _ = os.path.splitext(name)
        else:
            name = 'Untitled'
        return name

    def load(self, src):
        out, _ext = os.path.splitext(src)
        out = '{}.png'.format(out)

        import subprocess
        retcode = subprocess.call(['/usr/local/bin/gs', '-dNOPAUSE', '-dBATCH',
#                                   '-q',
                                    '-r150',
                                    '-dUseCropBox',
                                   '-sDEVICE=png256',
                                    '-sOutputFile={}'.format(out), src])
        if retcode == 0:
            self.table_image_source = out


    def _get_table_image(self):
        return ImageResource(
                             self.table_image_source
                             )
    def traits_view(self):
        v = View(UItem('table_image',
                       style='custom',
                       width=700,
                       height=500,
                       editor=ImageEditor(scrollable=True,
                                          scale=False
                                          )))
        return v

class SCLFTableEditor(TableEditor):
    pass
#============= EOF =============================================
