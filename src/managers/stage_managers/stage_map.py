'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import HasTraits, Str, Property, Float, List, Enum
from traitsui.api import View, Item, TabularEditor, HGroup

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.helpers.filetools import parse_file
from traitsui.tabular_adapter import TabularAdapter
class SampleHole(HasTraits):
    id = Str
    x = Float
    y = Float
    render = Str
    shape = Str
    dimension = Float

class SampleHoleAdapter(TabularAdapter):
    columns = [('ID', 'id'),
               ('X', 'x'), ('Y', 'y'),
                ('Render', 'render')]

class StageMap(HasTraits):
    file_path = Str
    #holes = Dict
    name = Property(depends_on='file_path')
    bitmap_path = Property(depends_on='file_path')
#    valid_holes = None
#    use_valid_holes = True
    #holes = Property
    sample_holes = List(SampleHole)

    g_dimension = Float(enter_set=True, auto_set=False)
    g_shape = Enum('circle', 'square')

    def get_hole_pos(self, key):
        return next(((h.x, h.y) for h in self.sample_holes if h.id == key), None)

#    def _get_holes(self):
#        keys = [s.id for s in self.sample_holes]
#        values = [(s.x, s.y) for s in self.sample_holes]
#        return dict((keys, values))

    def _get_bitmap_path(self):

        name, _ext = os.path.splitext(self.name)
        root, _path = os.path.split(self.file_path)
        name = '.'.join([name, 'png'])
        return os.path.join(root, name)

    def _get_name(self):
	    name= os.path.basename(self.file_path)
	    name, _ext = os.path.splitext(name)
	    return name
        
    def __init__(self, *args, **kw):
        super(StageMap, self).__init__(*args, **kw)
        self.load()

    def _g_dimension_changed(self):
        for h in self.sample_holes:
            h.dimension = self.g_dimension
        self._save_()


    def _g_shape_changed(self):
        for h in self.sample_holes:
            h.shape = self.g_shape
        self._save_()

    def _save_(self):
        pass
#        with open(self.file_path, 'r') as f:
#            lines = [line for line in f]
#
#        lines[0] = '{},{}\n'.format(self.g_shape, self.g_dimension)
#        with open(self.file_path, 'w') as f:
#            f.writelines(lines)

    def load(self):
        lines = parse_file(self.file_path)
        shape, dimension = lines[0].split(',')
        self.g_shape = shape
        self.g_dimension = float(dimension)

        valid_holes = lines[1].split(',')
        for hi, line in enumerate(lines[2:]):
            try:
                hole, x, y = line.split(',')
            except ValueError:
                x, y = line.split(',')
                hole = str(hi + 1)

            self.sample_holes.append(SampleHole(id=hole,
                                                 x=float(x),
                                                 y=float(y),
                                                 render='x' if hole in valid_holes else '',
                                                 shape=shape,
                                                 dimension=float(dimension)

                                                 ))

#============= views ===========================================
    def traits_view(self):
#        cols = [ObjectColumn(name = 'id'),
#              ObjectColumn(name = 'x'),
#              ObjectColumn(name = 'y'),
#              CheckboxColumn(name = 'render')
#              ]
#        editor = TableEditor(columns = cols)


        editor = TabularEditor(adapter=SampleHoleAdapter())
        v = View(
                 HGroup(Item('g_shape', show_label=False),
                        Item('g_dimension', show_label=False)
                        ),

                 Item('sample_holes',
                      show_label=False, editor=editor),
                 height=500, width=250,
                 resizable=True
                 )
        return v
#============= EOF =============================================
