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
from traits.api import HasTraits, Str, Property, CFloat, Float, List, Enum, Button, on_trait_change
from traitsui.api import View, Item, TabularEditor, HGroup

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.helpers.filetools import parse_file
from traitsui.tabular_adapter import TabularAdapter
from src.helpers.paths import hidden_dir
import pickle
from src.loggable import Loggable
from affine import AffineTransform


class SampleHole(HasTraits):
    id = Str
    x = Float
    y = Float
    x_cor = CFloat(0)
    y_cor = CFloat(0)
    render = Str
    shape = Str
    dimension = Float


class SampleHoleAdapter(TabularAdapter):
    columns = [('ID', 'id'),
               ('X', 'x'), ('Y', 'y'),
               ('XCor', 'x_cor'), ('YCor', 'y_cor'),
                ('Render', 'render')]


class StageMap(Loggable):
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

    clear_corrections = Button

    def map_to_uncalibration(self, pos, cpos, rot):
        a = AffineTransform()
        a.translate(-cpos[0], -cpos[1])
        a.translate(*cpos)
        a.rotate(-rot)
        a.translate(-cpos[0], -cpos[1])

        pos = a.transformPt(pos)
        return pos

    def map_to_calibration(self, pos, cpos, rot, translate=None):
        a = AffineTransform()
        if translate:
            a.translate(*translate)

        a.translate(*cpos)
        a.rotate(rot)
        a.translate(-cpos[0], -cpos[1])
        a.translate(*cpos)

        pos = a.transformPt(pos)
        return pos

    def _get_hole(self, key):
        return next((h for h in self.sample_holes if h.id == key), None)

    def get_hole_pos(self, key):
        return next(((h.x, h.y)
                     for h in self.sample_holes if h.id == key), None)

    def get_corrected_hole_pos(self, key):
        return next(((h.x_cor, h.y_cor)
                     for h in self.sample_holes if h.id == key), None)

    def load_correction_file(self):
        p = os.path.join(hidden_dir, '{}_correction_file'.format(self.name))
        if os.path.isfile(p):
            cors = None
            with open(p, 'rb') as f:
                try:
                    cors = pickle.load(f)
                except pickle.PickleError, e:
                    print e

            if cors:

                self.info('loaded correction file {}'.format(p))
                for i, x, y in cors:
                    h = self._get_hole(i)
                    if x is not None and y is not None:
                        h.x_cor = x
                        h.y_cor = y

    @on_trait_change('clear_corrections')
    def clear_correction_file(self):
        p = os.path.join(hidden_dir, '{}_correction_file'.format(self.name))
        if os.path.isfile(p):
            os.remove(p)
            self.info('removed correction file {}'.format(p))

        for h in self.sample_holes:
            h.x_cor = 0
            h.y_cor = 0

    def dump_correction_file(self):

        p = os.path.join(hidden_dir, '{}_correction_file'.format(self.name))
        with open(p, 'wb') as f:
            pickle.dump([(h.id, h.x_cor, h.y_cor)
                         for h in self.sample_holes], f)

        self.info('saved correction file {}'.format(p))

    def set_hole_correction(self, hn, x_cor, y_cor):
        hole = next((h for h in self.sample_holes if h.id == hn), None)
        if hole is not None:
            hole.x_cor = x_cor
            hole.y_cor = y_cor

    def _get_hole_by_position(self, x, y, tol=None):
        if tol is None:
            tol = self.g_dimension

        pythag = lambda hi:((hi.x - x) ** 2 + (hi.y - y) ** 2) ** 0.5
        holes = [(hole, pythag(hole)) for hole in self.sample_holes
                 if abs(hole.x - x) < tol and abs(hole.y - y) < tol]
        if holes:
            #sort holes by deviation 
            sorted(holes, lambda a, b: cmp(a[1], b[1]))
            return holes[0]

    def _get_bitmap_path(self):

        name, _ext = os.path.splitext(self.name)
        root, _path = os.path.split(self.file_path)
        name = '.'.join([name, 'png'])
        return os.path.join(root, name)

    def _get_name(self):
        name = os.path.basename(self.file_path)
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
        if not lines:
            return
        shape, dimension = lines[0].split(',')
        self.g_shape = shape
        self.g_dimension = float(dimension)

        valid_holes = lines[1].split(',')
        for hi, line in enumerate(lines[2:]):
            if not line.startswith('#'):
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
                 HGroup(Item('clear_corrections', show_label=False)),
                 HGroup(Item('g_shape'),
                        Item('g_dimension'), show_labels=False
                        ),

                 Item('sample_holes',
                      show_label=False, editor=editor),
                 height=500, width=250,
                 resizable=True,
                 title=self.name
                 )
        return v
#============= EOF =============================================
