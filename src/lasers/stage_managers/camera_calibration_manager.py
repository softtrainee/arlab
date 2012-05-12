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



#============= enthought library imports ======================
from traits.api import HasTraits, on_trait_change, Range, Bool, List, Str, Int, Float, Button, Instance
from traitsui.api import View, Item, Group, HGroup, VGroup, TableEditor, Handler
from src.image.image_editor import ImageEditor
from src.image.image import Image
from traitsui.menu import OKButton, CancelButton
from traitsui.extras.checkbox_column import CheckboxColumn
from traitsui.table_column import ObjectColumn
from src.managers.manager import Manager


#============= standard library imports =======================

#============= local library imports  =========================
class Polygon(HasTraits):
    enabled = Bool(True)
    name = Str
    width = Int
    height = Int
    points = List
class MHandler(Handler):
    def closed(self, info, is_ok):
        info.object.closed(info.ui.result)
        return True

class CameraCalibrationManager(Manager):
    image = Instance(Image)
    snapshot = Button
    polygons = List
    pxpercmx = Int
    pxpercmy = Int
    target_size = Float(0.5, enter_set=True, auto_set=False) #cm
    n = Int
    threshold = Range(0, 255, 100)
    cond = None

    def closed(self, result):
        self.result = result
        if self.cond:
            self.cond.notify()
            self.cond.release()

    @on_trait_change('polygons:enabled')
    def update(self, object, name, old, new):
        skip = [i for i, p in enumerate(self.polygons) if not p.enabled]

        self.process_image(skip=skip)

    def process_image(self, skip=None):
        im = self.image

        if skip is None:
            self.polygons = []

        polygons = im.polygonate(self.threshold,
                                 min_area=20,
                                 skip=skip, line_width=2)

        widths = []
        heights = []
        for i, p in enumerate(polygons):
            #this calculation assumes 4 points 
            print len(p), 'points'

            if len(p) != 4:
                continue

            p0 = p[0]
            p1 = p[1]
            p2 = p[2]
            p3 = p[3]

            dx = p0.x - p1.x
            dy = p0.y - p1.y
            l1 = (dx ** 2 + dy ** 2) ** 0.5

            dx = p2.x - p3.x
            dy = p2.y - p3.y
            l2 = (dx ** 2 + dy ** 2) ** 0.5

            dx = p1.x - p2.x
            dy = p1.y - p2.y
            l3 = (dx ** 2 + dy ** 2) ** 0.5

            dx = p3.x - p0.x
            dy = p3.y - p0.y
            l4 = (dx ** 2 + dy ** 2) ** 0.5

            #width and height maybe switched check order of points
            print p0.x, p1.x, p2.x, p3.x
            print p0.y, p1.y, p2.y, p3.y

            width = (l1 + l2) / 2.0
            height = (l3 + l4) / 2.0

            widths.append(width)
            heights.append(height)
            if skip is None:
                self.polygons.append(Polygon(name='{}'.format(i),
                                             width=width,
                                             height=height,
                                             points=p
                                             ))
        try:
            n = len(polygons)
            self.n = n

            #also calc pxpercm using polygon separation
            self.pxpercmx = int(sum(widths) / float(n) / self.target_size)
            self.pxpercmy = int(sum(heights) / float(n) / self.target_size)
        except ZeroDivisionError:
            pass

    def _target_size_changed(self):
        self.process_image(skip=[])

    def _threshold_changed(self):
        self.process_image()

    def _snapshot_fired(self):
        self.process_image()
        self.edit_traits(view='snapshot_view')
#    def calculate(self):
#        self.process_image()
#
#        do_later(self.edit_traits, view = 'snapshot_view')

#        info = self.edit_traits(view = 'snapshot_view')
#        if info.result:
#
#            print 'accept'
#            return self.pxpercmx, self.pxpercmy, self.polygons
#        else:
#            print 'decline'
    def edit_traits(self, *args, **kw):
        self.result = False
        if self.cond:
            self.cond.acquire()

        return super(CameraCalibrationManager, self).edit_traits(*args, **kw)

    def traits_view(self):
        v = View(Item('snapshot', show_label=False),

                 )
        return v

    def snapshot_view(self):
        results_grp = VGroup(
                             Group(Item('polygons', show_label=False, editor=TableEditor(columns=[ObjectColumn(name='name', editable=False),
                                                                                                  ObjectColumn(name='width', editable=False),
                                                                                                  ObjectColumn(name='height', editable=False),
                                                                                                  CheckboxColumn(name='enabled')
                                                                     ]))),
                             Item('target_size'),
                             Item('pxpercmx', style='readonly'),
                             Item('pxpercmy', style='readonly'),
                             Item('n', style='readonly')
                             )
        v = View(
                 HGroup(
                        VGroup(
                               Item('threshold', show_label=False),
                               Item('image', show_label=False,
                                    editor=ImageEditor()),
                               ),
                        results_grp
                        ),
                 handler=MHandler,
               title=self.title,
               resizable=True,
               buttons=[OKButton, CancelButton],
#               kind = 'livemodal'
               )
        return v

    def image_factory(self, path=None, src=None):
        im = Image()

#        if src is not None:
#            im.source_frame = src
#            im.frames.append(src)
#        else:
#            im.load(path)
        im.load('/Users/Ross/target3.png')
        self.image = im
        return im


if __name__ == '__main__':

    c = CameraCalibrationManager()
    im = Image()
    im.load('/Users/Ross/target3.png')
    c.title = 'target3.png'
    c.image = im
    c.configure_traits()
#============= EOF ============================================
