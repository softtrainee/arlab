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
from traits.api import HasTraits, Instance, Any, Button
from traitsui.api import View, Item, Controller, UItem, HGroup
from chaco.api import HPlotContainer, OverlayPlotContainer
from enable.component_editor import ComponentEditor
from pyface.api import FileDialog, OK
#============= standard library imports ========================
from lxml.etree import ElementTree, Element
from chaco.plot import Plot
from chaco.array_plot_data import ArrayPlotData
from numpy import linspace, cos, sin, pi
import os
import csv
from chaco.data_label import DataLabel
from src.paths import paths
from chaco.plot_graphics_context import PlotGraphicsContext
from traitsui.menu import Action
from pyface.timer.do_later import do_later
import math
#============= local library imports  ==========================
class myDataLabel(DataLabel):
    label_position = Any
    show_label_coords = False
    marker_visible = False
    label_position = 'center'
    border_visible = False

class GraphicGeneratorController(Controller):
    def save(self, info):
        self.model.save()

    def traits_view(self):
        w, h = 750, 750
        v = View(
                 UItem('container', editor=ComponentEditor(), style='custom'),
                 width=w + 2,
                 height=h + 56,
                 resizable=True,
                 buttons=[Action(name='Save', action='save')]
                 )
        return v

class GraphicModel(HasTraits):
    container = Instance(OverlayPlotContainer)
    def save(self, path=None):
#        print self.container.bounds

        if path is None:
            dlg = FileDialog(action='save as', default_directory=paths.data_dir)
            if dlg.open() == OK:
                path = dlg.path

        if path is not None:
            if not path.endswith('.png'):
                path = '{}.png'.format(path)

            c = self.container.components[0]
            gc = PlotGraphicsContext((int(c.outer_width), int(c.outer_height)))
#            c.use_backbuffer = False

            c.x_axis.visible = False
            c.y_axis.visible = False

            gc.render_component(c)
#            c.use_backbuffer = True
            gc.save(path)

    def load(self, path):
        parser = ElementTree(file=open(path, 'r'))
        circles = parser.find('circles')
        outline = parser.find('outline')

        bb = outline.find('bounding_box')
        bs = bb.find('width'), bb.find('height')
        w, h = map(lambda b:float(b.text), bs)


        data = ArrayPlotData()
        p = Plot(data=data, padding=2)
        p.x_grid.visible = False
        p.y_grid.visible = False
        p.x_axis_visible = False
        p.y_axis_visible = False
        p.index_range.low_setting = -w / 2
        p.index_range.high_setting = w / 2

        p.value_range.low_setting = -h / 2
        p.value_range.high_setting = h / 2

        thetas = linspace(0, 2 * pi)

        radius = circles.find('radius').text
        radius = float(radius)

        face_color = circles.find('face_color')
        if face_color is not None:
            face_color = face_color.text
        else:
            face_color = 'white'

        for i, pp in enumerate(circles.findall('point')):
            x, y, l = pp.find('x').text, pp.find('y').text, pp.find('label').text

            # load hole specific attrs
            r = pp.find('radius')
            if r is None:
                r = radius
            else:
                r = float(r.text)

            fc = pp.find('face_color')
            if fc is None:
                fc = face_color
            else:
                fc = fc.text

            x, y = map(float, (x, y))
            xs = x + r * sin(thetas)
            ys = y + r * cos(thetas)

            xn, yn = 'px{:03n}'.format(i), 'py{:03n}'.format(i)
            data.set_data(xn, xs)
            data.set_data(yn, ys)

            plot = p.plot((xn, yn),
                   face_color=fc,
                   type='polygon',
                   )[0]

            label = myDataLabel(component=plot,
                              data_point=(x, y),
                              label_text=l,
                              bgcolor='transparent',

                              )
            plot.overlays.append(label)

        self.container.add(p)

    def _container_default(self):
        c = OverlayPlotContainer(bgcolor='green',
                                 )
        return c

def make_xml(path, offset=100, default_bounds=(50, 50),
             default_radius=3
             ):
    '''
        convert a csv into an xml
        
        use blank line as a group marker
        circle labels are offset by ``offset*group_id``
        ie. group 0. 1,2,3
            group 1. 101,102,103
    '''
    root = Element('root')
    out = '{}_from_csv.xml'.format(os.path.splitext(path)[0])

    outline = Element('outline')
    bb = Element('bounding_box')
    width, height = Element('width'), Element('height')
    width.text, height.text = map(str, default_bounds)
    bb.append(width)
    bb.append(height)

    outline.append(bb)
    root.append(outline)

    circles = Element('circles')
    radius = Element('radius')
    radius.text = str(default_radius)
    circles.append(radius)

    face_color = Element('face_color')
    face_color.text = 'white'
    circles.append(face_color)

    root.append(circles)

    i = 0
    off = 0
    reader = csv.reader(open(path, 'r'), delimiter=',')
    writer = open(path + 'angles.txt', 'w')
    _header = reader.next()

    for k, row in enumerate(reader):
        row = map(str.strip, row)
        if row:
            e = Element('point')
            x, y, l = Element('x'), Element('y'), Element('label')
            x.text = row[0]
            y.text = row[1]

            a = math.degrees(math.atan2(float(y.text), float(x.text)))
            writer.write('{} {}\n'.format(k + 1, a))
            l.text = str(i + 1 + off)

            e.append(l)
            e.append(x)
            e.append(y)
            circles.append(e)
            i += 1
        else:
            # use blank rows as group markers
            off += offset
            i = 0

    tree = ElementTree(root)
    tree.write(out,
               xml_declaration=True,
               method='xml',
               pretty_print=True)
    return out

def open_txt(p):
    gm = GraphicModel()
    p = make_xml(p,
                 default_radius=0.0175,
                 default_bounds=(1, 1))

#    p = '/Users/ross/Sandbox/graphic_gen_from_csv.xml'
    gm.load(p)
    gcc = GraphicGeneratorController(model=gm)
    return gcc
if __name__ == '__main__':
    gm = GraphicModel()
    p = '/Users/ross/Sandbox/2mmirrad.txt'
    p = '/Users/ross/Sandbox/2mmirrad_ordered.txt'
    p = '/Users/ross/Sandbox/1_75mmirrad_ordered.txt'
    p = '/Users/ross/Sandbox/1_75mmirrad_ordered.txt'
    p = '/Users/ross/Pychrondata_diode/setupfiles/irradiation_tray_maps/0_75mmirrad_ordered1.txt'
#    p = '/Users/ross/Sandbox/graphic_gen.csv'
#    gcc1 = open_txt(p)
#    do_later(gcc1.edit_traits)

    p = '/Users/ross/Sandbox/1_75mmirrad.txt'
    p = '/Users/ross/Pychrondata_diode/setupfiles/irradiation_tray_maps/1_75mm_3level'
#    p = '/Users/ross/Pychrondata_diode/setupfiles/irradiation_tray_maps/0_75mmirrad.txt'

#    p = '/Users/ross/Pychrondata_diode/setupfiles/irradiation_tray_maps/0_75mmirrad_continuous.txt'
#    p = '/Users/ross/Pychrondata_diode/setupfiles/irradiation_tray_maps/newtrays/2mmirrad_continuous.txt'
    gcc = open_txt(p)
    gcc.configure_traits()

#============= EOF =============================================
