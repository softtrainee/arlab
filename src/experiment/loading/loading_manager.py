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
from traits.api import HasTraits, cached_property, List, Str, \
     Property, Int, Event, Any, Bool
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.canvas.canvas2D.loading_canvas import LoadingCanvas
#============= standard library imports ========================
#============= local library imports  ==========================
from itertools import groupby
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from chaco.pdf_graphics_context import PdfPlotGraphicsContext
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def make_bound(st):
    if len(st) > 1:
        s = '{}-{}'.format(st[0], st[-1])
    else:
        s = '{}'.format(st[0])
    return s

def make_position_str(pos):
    s = ''
    if pos:
        pos = sorted(pos)
        pp = pos[0]
        stack = [pp]
        ss = []

        for pi in  pos[1:]:
            if not pp + 1 == pi:
                ss.append(make_bound(stack))
                stack = []

            stack.append(pi)
            pp = pi

        if stack:
            ss.append(make_bound(stack))

        s = ','.join(ss)
    return s

class LoadPosition(HasTraits):
    labnumber = Str
    sample = Str
    positions = List
    level = Str
    irradiation = Str
    irrad_position = Int

    irradiation_str = Property
    position_str = Property(depends_on='positions[]')

    def _get_position_str(self):
        return make_position_str(self.positions)

    def _get_irradiation_str(self):
        return '{} {}{}'.format(self.irradiation,
                                self.level,
                                self.irrad_position)

class ComponentFlowable(Flowable):
    component = None
    def __init__(self, component=None):
        self.component = component
        Flowable.__init__(self)

    def _compute_scale(self, page_width, page_height,
                            width, height):

        aspect = float(width) / float(height)

        if aspect >= page_width / page_height:
            # We are limited in width, so use widths to compute the scale
            # factor between pixels to page units.  (We want square pixels,
            # so we re-use this scale for the vertical dimension.)
            scale = float(page_width) / float(width)
        else:
            scale = page_height / height

        self._scale = scale
        return scale

    def wrap(self, aW, aH):
        cw, ch = aW, aH
        if self.component:
            cw, ch = self.component.outer_bounds
            scale = self._compute_scale(aW, aH, cw, ch)

        return cw * scale, ch * scale

    def draw(self):
        if self.component:
            gc = PdfPlotGraphicsContext(pdf_canvas=self.canv)

            scale = self._scale
            gc.scale_ctm(scale, scale)
            self.component.draw(gc)

class LoadingManager(IsotopeDatabaseManager):

    tray = Str
    trays = List
    load_name = Str

    labnumber = Str
    labnumbers = Property(depends_on='level')

    irradiation_hole = Str
    sample = Str

    positions = List

    # table signal/events
    refresh_table = Event
    scroll_to_row = Int
    selected_positions = Any

    db_load_name = Str
    loads = List

    group_positions = Bool
    show_group_positions = Bool(False)
#     def save_loading(self):
#         path = '/Users/ross/Sandbox/load_001.pdf'
#         if path:
#             doc = SimpleDocTemplate(path)
#             fl = [ComponentFlowable(component=self.canvas),
#                 ]
#             doc.build(fl)

    def setup(self):
        self.populate_default_tables()

        ls = self._get_loads()
        if ls:
            self.loads = ls

        ts = self._get_trays()
        if ts:
            self.trays = ts

        ls = self._get_last_load()

    def _get_loads(self):
        loads = self.db.get_loads()
        if loads:
            return [li.name for li in loads]

    def _get_trays(self):
        trays = self.db.get_load_holders()
        if trays:
            ts = [ti.name for ti in trays]
            return ts

    def _get_last_load(self):
        lt = self.db.get_loadtable()
        if lt:

            self.db_load_name = lt.name
            if lt.holder_:
#                 self.tray = lt.holder_.name

                self.load_load(lt)

        return self.db_load_name

    def make_canvas(self, new, editable=True):
        db = self.db
        lt = db.get_loadtable(new)
        c = LoadingCanvas(
                          view_x_range=(-2, 2),
                          view_y_range=(-2, 2),
                          editable=editable
                          )
        self.canvas = c
        if lt:
            h = lt.holder_.name
            c.load_tray_map(h)
            for pi in lt.loaded_positions:
                item = c.scene.get_item(str(pi.position))
                if item:
                    item.fill = True
                    item.identifier = pi.lab_identifier

            for pi in lt.measured_positions:
                item = c.scene.get_item(str(pi.position))
                if item:
                    if pi.is_degas:
                        item.degas_indicator = True
                    else:
                        item.measured_indicator = True
        return c

    def load_load(self, loadtable, group_labnumbers=True):
        if isinstance(loadtable, str):
            loadtable = self.db.get_loadtable(loadtable)

        self.positions = []
        self.tray = loadtable.holder_.name
        for ln, poss in groupby(loadtable.loaded_positions,
                                        key=lambda x:x.lab_identifier):
            pos = []
            for pi in poss:
                pid = pi.position
                item = self.canvas.scene.get_item(str(pid))
                if item:
                    item.fill = True
#                     print item
                    item.add_text(ln, oy=-10)

                pos.append(pid)

            if group_labnumbers:
                self._add_position(ln, pos)
            else:
                for pi in pos:
                    self._add_position(ln, [pi])


    def _add_position(self, ln, pos):
        ln = self.db.get_labnumber(ln)
        ip = ln.irradiation_position
        level = ip.level
        irrad = level.irradiation

        sample = ln.sample.name if ln.sample else ''

        lp = LoadPosition(labnumber=ln.identifier,
              sample=sample,
              irradiation=irrad.name,
              level=level.name,
              irrad_position=int(ip.position),
              positions=pos
              )
        self.positions.append(lp)


    def save(self):
        db = self.db
        if self.load_name:
            lln = self._get_last_load()
            if self.load_name == lln:
                return 'duplicate name'
            else:
                self.info('adding load {} to database'.format(self.load_name))
                db.add_load(self.load_name, holder=self.tray)
                db.commit()

                ls = self._get_loads()
                self.loads = ls
                self._get_last_load()
                self.load_name = ''

        else:
            lt = db.get_loadtable(name=self.db_load_name)

            sess = db.get_session()
            for li in lt.loaded_positions:
                sess.delete(li)

            db.flush()
            for pi in self.positions:
                ln = pi.labnumber
                self.info('updating positions for {} {}'.format(lt.name, ln))
                for pp in pi.positions:
                    i = db.add_load_position(ln, position=pp)
                    lt.loaded_positions.append(i)

            db.commit()

    @cached_property
    def _get_labnumbers(self):
        level = self.db.get_irradiation_level(self.irradiation, self.level)
        if level:
#             self._positions = [str(li.position) for li in level.positions]
            return sorted([li.labnumber.identifier for li in level.positions])
        else:
            return []

    def _labnumber_changed(self):
        level = self.db.get_irradiation_level(self.irradiation, self.level)
        if level:
            pos = next((pi for pi in level.positions
                  if pi.labnumber.identifier == self.labnumber), None)
            if pos is not None:
                self.irradiation_hole = str(pos.position)

                sample = pos.labnumber.sample
                if sample:
                    self.sample = sample.name


#============= EOF =============================================
