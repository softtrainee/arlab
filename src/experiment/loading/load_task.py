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
from traits.api import on_trait_change, Any, List
# from traitsui.api import View, Item
from pyface.tasks.task_layout import PaneItem, TaskLayout
from pyface.constant import CANCEL, NO
from pyface.tasks.action.schema import SToolBar
#============= standard library imports ========================
#============= local library imports  ==========================
# from src.envisage.tasks.base_task import BaseManagerTask
# from pyface.tasks.task_window_layout import TaskWindowLayout
# from src.envisage.tasks.editor_task import EditorTask
# from src.experiment.tasks.experiment_editor import ExperimentEditor
# from src.paths import paths
# import hashlib
# import os
# from src.helpers.filetools import add_extension
# from src.ui.gui import invoke_in_main_thread
# from apptools.preferences.preference_binding import bind_preference
from src.envisage.tasks.base_task import BaseManagerTask
from src.experiment.loading.panes import LoadPane, LoadControlPane, LoadTablePane
from src.canvas.canvas2D.loading_canvas import LoadingCanvas
# from src.experiment.isotope_database_manager import IsotopeDatabaseManager

# from itertools import groupby
from src.experiment.loading.actions import SaveLoadingAction
# from pyface.image_resource import ImageResource
# from src.paths import paths
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.flowables import PageBreak, Flowable
from reportlab.platypus.doctemplate import SimpleDocTemplate, BaseDocTemplate, \
    PageTemplate, FrameBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from chaco.pdf_graphics_context import PdfPlotGraphicsContext
from src.experiment.loading.loading_manager import LoadingManager, LoadPosition, \
    ComponentFlowable
from reportlab.platypus.frames import Frame


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
        self.table_pane = LoadTablePane(model=self.manager)
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
        path = '/Users/ross/Sandbox/load_001.pdf'
        if path:
            doc = BaseDocTemplate(path,
                                  leftMargin=0.25 * inch,
                                  rightMargin=0.25 * inch,
#                                   _pageBreakQuick=0,
                                  showBoundary=1)
#             doc = SimpleDocTemplate(path)

            man = self.manager

            n = len(man.positions)
            idx = int(round(n / 2.))

            p1 = man.positions[:idx]
            p2 = man.positions[idx:]
#
            t1 = self._make_table(p1)
            t2 = self._make_table(p2)
            fl = [ComponentFlowable(component=self.canvas),
                  FrameBreak(),
                  t1,
                  FrameBreak(),
                  t2
                  ]

            # make 3 frames top, lower-left, lower-right
            lm = doc.leftMargin
            bm = doc.bottomMargin + doc.height * .333

            fw = doc.width
            fh = doc.height * 0.666
            top = Frame(lm, bm, fw, fh)

            fw = doc.width / 2.
            fh = doc.height * 0.333
            bm = doc.bottomMargin
            lbottom = Frame(lm, bm, fw, fh, showBoundary=True)
            rbottom = Frame(lm + doc.width / 2., bm, fw, fh)

            template = PageTemplate(frames=[top, lbottom, rbottom])
            doc.addPageTemplates(template)

            doc.build(fl)

    def _make_table(self, positions):
        data = [('L#', 'Irradiation', 'Sample', 'Positions')]
#         man = self.manager

        ts = TableStyle()
        ts.add('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)

        ts.add('FONTSIZE', (-3, 1), (-1, -1), 8)
        ts.add('VALIGN', (-3, 1), (-1, -1), 'MIDDLE')
#         positions = positions * 15

        for idx, pi in enumerate(positions):
            row = (pi.labnumber, pi.irradiation_str, pi.sample,
                   pi.position_str)
            data.append(row)
            if idx % 2 == 0:
                ts.add('BACKGROUND', (0, idx + 1), (-1, idx + 1),
                        colors.lightgrey)

        cw = map(lambda x: mm * x, [12, 20, 22, 40])

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
                          view_x_range=(-2.2, 2.2),
                          view_y_range=(-2.2, 2.2),

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
#             irrad_str = '{} {}{}'.format(man.irradiation,
#                                        man.level,
#                                        man.irradiation_hole
#                                        )

            pos = next((pi for pi in  man.positions
                       if pi.labnumber == man.labnumber), None)

            pid = int(new.identifier)

            new.add_text(man.labnumber, oy=-10)
            if pos is not None:
                if new.fill:
                    if pid in pos.positions:
                        pos.positions.remove(pid)
                        new.fill = False
                        new.clear_text()
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
                                  irradiation=man.irradiation,
                                  level=man.level,
                                  irrad_position=int(man.irradiation_hole),
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
#     def save_loading2(self):
# #         path = self.save_file_dialog()
#         path = '/Users/ross/Sandbox/load_001.pdf'
#         if path:
#
#             from chaco.pdf_graphics_context import PdfPlotGraphicsContext
#
# #             doc = SimpleDocTemplate(path)
# #             fl = [ComponentFlowable(component=self.canvas),
# #                   ]
# #             doc.save()
#             w, h = letter
#             gc = PdfPlotGraphicsContext(filename=path,
#                                         pagesize='letter',
# #                                         dest_box=(0.5, hh / 2. - 0.5,
# #                                                   -0.5,
# #                                                   hh / 2.)
#                                         )
#             component = self.canvas
# #             component.use_backbuffer = False
#
#             man = self.manager
#
#             n = len(man.positions)
#             idx = int(round(n / 2.))
#             p1 = man.positions[:idx + 1]
#             p2 = man.positions[idx - 1:]
# #
#             t1 = self._make_table(p1)
#             t2 = self._make_table(p2)
#
#             single_page = True
#             if not single_page:
#
#                 gc.render_component(component)
#                 gc.gc.showPage()
#                 t1.wrapOn(gc.gc, w, h)
#
#                 hh = h - t1._height - 0.5 * inch
#                 t1.drawOn(gc.gc, 0.5 * inch, hh)
#
#                 t2.wrapOn(gc.gc, w, h)
#
#                 hh = h - t2._height - 0.5 * inch
#                 t2.drawOn(gc.gc, 0.5 * inch + w / 2.0, hh)
#
#             else:
#                 hh = h - component.height - 1 * inch
#                 left = t1.split(w, hh)
#                 right = t2.split(w, hh)
#
#                 t = left[0]
#                 t.wrapOn(gc.gc, w, hh)
#                 t.drawOn(gc.gc, 0, 0)
#
#                 th = t._height
#
#                 t = right[0]
#                 t.wrapOn(gc.gc, w, hh)
#
#                 dh = th - t._height
#                 t.drawOn(gc.gc, w / 2.0 - 0.4 * inch, dh)
#
#                 gc.render_component(component)
#                 gc.gc.showPage()
#
#                 if len(left) > 1:
#                     t = left[1]
#                     th = t._height
#                     t.wrapOn(gc.gc, w, h)
#                     t.drawOn(gc.gc, 0.5 * inch,
#                              h - 0.5 * inch - th)
#
#                     if len(right) > 1:
#                         t = right[1]
#                         t.wrapOn(gc.gc, w, h - inch)
#                         t.drawOn(gc.gc, w / 2 + 0.5 * inch,
#                                  h - 0.5 * inch - th)
#             gc.save()
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
