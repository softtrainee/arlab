#===============================================================================
# Copyright 2011 Jake Ross
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
    interpolated = False
    def has_correction(self):
#        print self.id, self.x_cor, self.y_cor
        return True if (abs(self.x_cor) > 1e-6
                and abs(self.y_cor) > 1e-6) else False

class SampleHoleAdapter(TabularAdapter):
    columns = [('ID', 'id'),
               ('X', 'x'), ('Y', 'y'),
               ('XCor', 'x_cor'), ('YCor', 'y_cor'),
                ('Render', 'render')]

    def set_text(self, obj, trait, row, column, txt):
        if column in [3, 4]:
            try:
                txt = float(txt)
            except:
                txt = '0'

        setattr(getattr(obj, trait)[row], self.columns[column][1], txt)


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

    #should always be N,E,S,W,center
    calibration_holes = None

    def interpolate_noncorrected(self):
        self.info('iteratively fill in non corrected holes')
        n = len(self.sample_holes)
        for i in range(2):
            self._interpolate_noncorrected()

            g = len([h for h in self.sample_holes
                     if h.has_correction()])

            if g == n:
                break
            self.info('iteration {}, total={}'.format(i + 1, g))
        if g < n:
            self.info('{} holes remain noncorrected'.format(n - g))
        else:
            self.info('all holes now corrected')

    def get_interpolated_position(self, holenum):
        h = self._get_hole(holenum)
        return self._calculated_interpolated_position(h)

    def _interpolate_noncorrected(self):
        self.sample_holes.reverse()
        for h in self.sample_holes:
            self._calculated_interpolated_position(h)

    def _calculated_interpolated_position(self, h):
        def _midpoint(a, b):
            mx = None
            my = None
#                    print a, b
            if a and b:
                dx = abs(a[0] - b[0])
                dy = abs(a[1] - b[1])
                mx = min(a[0], b[0]) + dx / 2.0
                my = min(a[1], b[1]) + dy / 2.0
            return mx, my

        spacing = abs(self.sample_holes[0].x - self.sample_holes[1].x)
        scalar = 1
        spacing *= scalar
        debug_hole = '216'
        nxs = []
        nys = []
        if not h.has_correction():
            #this hole does not have a correction value
            found = []
            #get the cardinal holes
            for rx, ry in [(0, 1),
                           (-1, 0), (1, 0),
                                (0, -1)
                          ]:

                x = h.x + rx * spacing#1.2 * self.g_dimension
                y = h.y + ry * spacing#1.2 * self.g_dimension

                hole = self._get_hole_by_corrected_position(x, y)

                if hole == h:
                    hole = None

                fo = None
                if hole is not None:
                    six, siy = hole.x_cor, hole.y_cor
                    if hole.has_correction():
                        fo = (six, siy)
                found.append(fo)

            rad = h.dimension
            for i, j in [(0, 3), (1, 2)]:
                mx, my = _midpoint(found[i], found[j])
                if mx is not None and my is not None:
                    #make sure the corrected value makes sense
                    #ie less than 1 radius from nominal hole
                    if (abs(mx - h.x) < rad
                            and abs(my - h.y) < rad):
                        nxs.append(mx)
                        nys.append(my)

            if not nxs:
#                #try iding using "triangulation"
                for i, j in [(0, 1), (0, 2), (3, 2), (3, 1)]:

                    x = found[i][0] if found[i] else None
                    y = found[j][1] if found[j] else None

                    if x and y:
                        if (abs(x - h.x) < rad
                                and abs(y - h.y) < rad):
                            nxs.append(x)
                            nys.append(y)

        nx, ny = (sum(nxs) / max(1, len(nxs)),
                    sum(nys) / max(1, len(nys)))

        if nx and ny:
            h.interpolated = True
#            print h.id
            h.x_cor = nx
            h.y_cor = ny

        return nx, ny

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
        return next((h for h in self.sample_holes if h.id == str(key)), None)

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
                    if h is not None:
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
        return self._get_hole_by_pos(x, y, 'x', 'y', tol)

    def _get_hole_by_corrected_position(self, x, y, tol=None):
        return self._get_hole_by_pos(x, y, 'x_cor', 'y_cor', tol)

    def _get_hole_by_pos(self, x, y, xkey, ykey, tol):
        if tol is None:
            tol = self.g_dimension * 0.75

        pythag = lambda hi, xi, yi:((hi.x - xi) ** 2 + (hi.y - yi) ** 2) ** 0.5
        holes = [(hole, pythag(hole, x, y)) for hole in self.sample_holes
                 if abs(getattr(hole, xkey) - x) < tol and abs(getattr(hole, ykey) - y) < tol]
        if holes:
#            #sort holes by deviation 
            holes = sorted(holes, lambda a, b: cmp(a[1], b[1]))
            return holes[0][0]

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

        #line 0 shape, dimension
        shape, dimension = lines[0].split(',')
        self.g_shape = shape
        self.g_dimension = float(dimension)

        #line 1 list of holes to default draw
        valid_holes = lines[1].split(',')

        #line 2 list of calibration holes
        #should always be N,E,S,W,center
        self.calibration_holes = lines[2].split(',')

        for hi, line in enumerate(lines[3:]):
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
#        cspacing = spacing
#        for i, e in enumerate(self.sample_holes[1:]):
#            s = self.sample_holes[i - 1]
#            if s.has_correction() and e.has_correction():
#                dx = abs(s.x_cor - e.x_cor)
#                dy = abs(s.y_cor - e.y_cor)
##                cspacing = (dx + dy) / 2.0
#                break

            #if the number of adjacent holes found is only 1
            #do a simple offset using 
#                nfound = [f for f in found if f is not None]
#                if len(nfound) == 1:
#                    f = nfound[0]
#                    ind = found.index(f)
#                    x = f[0]
#                    y = f[1]
#                    l = cspacing#spacing / scalar
#                    if ind == 0:
#                        nxs.append(x)
#                        nys.append(y - l)
#                    elif ind == 1:
#                        nxs.append(x + l)
#                        nys.append(y)
#                    elif ind == 2:
#                        nxs.append(x - l)
#                        nys.append(y)
#                    else:
#                        nxs.append(x)
#                        nys.append(y + l)

