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
from traits.api import HasTraits, on_trait_change, Any, Bool, Str, Property, \
    cached_property, List, Event, Int
# from traitsui.api import View, Item
from pyface.tasks.task_layout import PaneItem, TaskLayout, Splitter, Tabbed
#============= standard library imports ========================
#============= local library imports  ==========================
# from src.envisage.tasks.base_task import BaseManagerTask
# from pyface.tasks.task_window_layout import TaskWindowLayout
# from src.envisage.tasks.editor_task import EditorTask
# from src.experiment.tasks.experiment_editor import ExperimentEditor
# from src.paths import paths
# import hashlib
# import os
from pyface.constant import CANCEL, YES, NO
# from src.helpers.filetools import add_extension
# from src.ui.gui import invoke_in_main_thread
# from apptools.preferences.preference_binding import bind_preference
from src.envisage.tasks.base_task import BaseTask, BaseManagerTask
from src.experiment.loading.panes import LoadPane, LoadControlPane, LoadTable
from src.canvas.canvas2D.loading_canvas import LoadingCanvas
from src.experiment.isotope_database_manager import IsotopeDatabaseManager

from itertools import groupby
from pyface.tasks.action.schema import SToolBar
from src.experiment.loading.actions import SaveLoadingAction
from pyface.image_resource import ImageResource
from src.paths import paths
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.flowables import PageBreak, Flowable
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from chaco.pdf_graphics_context import PdfPlotGraphicsContext

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
    irradiation_str = Str
    sample = Str
    positions = List

    position_str = Property(depends_on='positions[]')
    def _get_position_str(self):
        return make_position_str(self.positions)

class LoadingManager(IsotopeDatabaseManager):

    tray = Str
    trays = List
    load_name = Str

    labnumber = Str
    labnumbers = Property(depends_on='level')

    irradiation_hole = Str
    sample = Str
    refresh_table = Event

    positions = List
    scroll_to_row = Int

    db_load_name = Str
    loads = List

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

    def load_load(self, loadtable):
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
                pos.append(pid)
            ln = self.db.get_labnumber(ln)
            ip = ln.irradiation_position
            level = ip.level
            irrad = level.irradiation

            sample = ln.sample.name if ln.sample else ''

            lp = LoadPosition(labnumber=ln.identifier,
                  sample=sample,
                  irradiation_str='{} {}{}'.format(irrad.name,
                                                   level.name,
                                                   ip.position),

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



# class ComponentFlowable(Flowable):
#     component = None
#     def __init__(self, component=None):
#         self.component = component
#         Flowable.__init__(self)
#
#
#     def draw(self):
#         print 'sefas', self.component, self.canv
#         if self.component:
#             print self.canv
#             gc = PdfPlotGraphicsContext(pdf_canvas=self.canv)
#             gc.render_component(self.component)


class LoadingTask(BaseManagerTask):
    name = 'Loading'
    load_pane = Any

    dirty = False
    control_pane = Any
    canvas = Any
    _positions = List
    tool_bars = [SToolBar(SaveLoadingAction(),
                          image_size=(32, 32)
                          )]

    def activated(self):
        self.manager.tray = 'A'
        self.manager.irradiation = 'NM-251'
        self.manager.level = 'H'
        self.manager.labnumber = '61311'

        self.manager.setup()

    def _manager_default(self):
        return LoadingManager()

    def _default_layout_default(self):
        return TaskLayout(
                          left=PaneItem('pychron.loading.controls'),
                          bottom=PaneItem('pychron.loading.positions')
                          )

    def prepare_destroy(self):
        pass

    def create_dock_panes(self):

        self.control_pane = LoadControlPane(model=self.manager)
        self.table_pane = LoadTable(model=self.manager)
#         self.irradiation_pane = LoadIrradiationPane(model=self.manager)
        return [self.control_pane,
                self.table_pane,
#                 self.irradiation_pane

                ]

    def create_central_pane(self):
        self.load_pane = LoadPane()
        return self.load_pane

    def save(self):
        self.manager.save()

    def save_loading(self):
#         path = self.save_file_dialog()
        path = '/Users/ross/Sandbox/load_001.pdf'
        if path:

            from chaco.pdf_graphics_context import PdfPlotGraphicsContext

#             doc = SimpleDocTemplate(path)
#             fl = [ComponentFlowable(component=self.canvas),
#                   ]
#             doc.save()
            w, h = letter
            gc = PdfPlotGraphicsContext(filename=path,
                                        pagesize='letter',
#                                         dest_box=(0.5, hh / 2. - 0.5,
#                                                   -0.5,
#                                                   hh / 2.)
                                        )
            component = self.canvas
#             component.use_backbuffer = False

            man = self.manager

            n = len(man.positions)
            idx = int(round(n / 2.))
            p1 = man.positions[:idx + 1]
            p2 = man.positions[idx - 1:]
#
            t1 = self._make_table(p1)
            t2 = self._make_table(p2)

            single_page = True
            if not single_page:

                gc.render_component(component)
                gc.gc.showPage()
                t1.wrapOn(gc.gc, w, h)

                hh = h - t1._height - 0.5 * inch
                t1.drawOn(gc.gc, 0.5 * inch, hh)

                t2.wrapOn(gc.gc, w, h)

                hh = h - t2._height - 0.5 * inch
                t2.drawOn(gc.gc, 0.5 * inch + w / 2.0, hh)

            else:
                hh = h - component.height - 1 * inch
                left = t1.split(w, hh)
                right = t2.split(w, hh)

                t = left[0]
                t.wrapOn(gc.gc, w, hh)
                t.drawOn(gc.gc, 0, 0)

                th = t._height

                t = right[0]
                t.wrapOn(gc.gc, w, hh)

                dh = th - t._height
                t.drawOn(gc.gc, w / 2.0 - 0.4 * inch, dh)

                gc.render_component(component)
                gc.gc.showPage()

                if len(left) > 1:
                    t = left[1]
                    th = t._height
                    t.wrapOn(gc.gc, w, h)
                    t.drawOn(gc.gc, 0.5 * inch,
                             h - 0.5 * inch - th)

                    if len(right) > 1:
                        t = right[1]
                        t.wrapOn(gc.gc, w, h - inch)
                        t.drawOn(gc.gc, w / 2 + 0.5 * inch,
                                 h - 0.5 * inch - th)
            gc.save()

    def _make_table(self, positions):
        data = [('L#', 'Irradiation', 'Sample', 'Positions')]
#         man = self.manager

        ts = TableStyle()
        ts.add('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)
#         positions = positions * 15

        for idx, pi in enumerate(positions):
            row = (pi.labnumber, pi.irradiation_str, pi.sample,
                   pi.position_str)
            data.append(row)
            if idx % 2 == 0:
                ts.add('BACKGROUND', (0, idx + 1), (-1, idx + 1),
                        colors.lightgrey)

        cw = map(lambda x: mm * x, [15, 25, 32, 23])

        rh = [mm * 5 for i in range(len(data))]
        t = Table(data,
                  colWidths=cw,
                  rowHeights=rh
                  )

        t.setStyle(ts)

        return t

    @on_trait_change('manager:db_load_name')
    def _load_changed(self):
        self.manager.load_load(self.manager.db_load_name)

    @on_trait_change('manager:tray')
    def _tray_changed(self):

        c = LoadingCanvas(
                          view_x_range=(-2, 2),
                          view_y_range=(-2, 2),

                          )
        c.load_tray_map(self.manager.tray)
        self.canvas = c
        self.load_pane.component = c

        self.manager.canvas = c

        self.manager.positions = []

    @on_trait_change('canvas:selected')
    def _update_selected(self, new):
        if not new:
            return

        man = self.manager
        if man.labnumber:
            irrad_str = '{} {}{}'.format(man.irradiation,
                                       man.level,
                                       man.irradiation_hole
                                       )

            pos = next((pi for pi in  man.positions
                       if pi.labnumber == man.labnumber), None)

            pid = int(new.identifier)
            if pos is not None:
                if new.fill:

                    if pid in pos.positions:
                        pos.positions.remove(pid)
                        new.fill = False
                    else:
                        npos = next((pi for pi in man.positions
                                    if pid in pi.positions), None)
                        if npos:
                            npos.positions.remove(pid)

                        pos.positions.append(pid)

                    if not pos.positions:
                        man.positions.remove(pos)
                else:
                    pos.positions.append(pid)

                    new.fill = True
            else:
                lp = LoadPosition(labnumber=man.labnumber,
                                irradiation_str=irrad_str,
                                sample=man.sample,
                                positions=[pid]
                                )
                man.positions.append(lp)
                new.fill = True

            man.refresh_table = True

    @on_trait_change('window:closing')
    def _prompt_on_close(self, event):
        '''
            Prompt the user to save when exiting.
        '''
        if self.dirty:
            result = self._confirmation('ffoo')

            if result in (CANCEL, NO):
                event.veto = True
            else:
                self._save()

#============= EOF =============================================
# if new in self._positions:
#                 new.fill = False
#                 self._positions.remove(new)
#             else:
#                 new.fill = True
#                 self._positions.append(new)
#                 new.labnumber = man.labnumber
#                 new.args = (man.labnumber, irrad_str, man.sample)
#
#             pos = sorted(self._positions,
#                          key=lambda x: int(x.identifier))
#
#             man.positions = []
#             for g, ps in groupby(pos, key=lambda x:x.labnumber):
#
#                 pi = ps.next()
#                 lp = LoadPosition(labnumber=pi.args[0],
#                                   irradiation_str=pi.args[1],
#                                   sample=pi.args[2],
#                                   positions=[pi.identifier]
#                                  )
#                 man.positions.append(lp)
#                 pp = int(pi.identifier)
#
#                 for pi in ps:
#                     pid = int(pi.identifier)
# #                     print g, pp, pi.identifier
#                     if pp is not None and pp + 1 != pid:
#                         lp = LoadPosition(labnumber=pi.args[0],
#                                           irradiation_str=pi.args[1],
#                                           sample=pi.args[2],
#                                           positions=[pid]
#                                          )
#                         man.positions.append(lp)
# #                         print 'new'
#                     else:
#                         lp.positions.append(pid)
#
#                     pp = int(pid)
#
#                 for i, pi in enumerate(man.positions):
#                     if int(new.identifier) in pi.positions:
#                         man.scroll_to_row = i
#                         break
