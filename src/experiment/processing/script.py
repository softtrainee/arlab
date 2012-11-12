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
from traits.api import HasTraits, Instance, Int, Any, Event, on_trait_change, Either, Float
from traitsui.api import View, Item, TableEditor
from pyface.timer.do_later import do_later
#============= standard library imports ========================
from sqlalchemy.sql.expression import and_
#============= local library imports  ==========================
from src.experiment.processing.database_manager import DatabaseManager
from src.experiment.processing.plotters.ideogram import Ideogram
from src.experiment.processing.analysis import Analysis
from src.database.records.isotope_record import IsotopeRecord
from src.graph.graph_container import HGraphContainer
from enable.component_editor import ComponentEditor
from chaco.pdf_graphics_context import PdfPlotGraphicsContext
from src.helpers.filetools import unique_path
import os
#from threading import Event as TEvent, Thread
#from src.viewable import ViewableHandler, Viewable

class Window(HasTraits):
    container = Instance(HGraphContainer, ())
    window_width = Either(Int, Float)
    window_height = Either(Int, Float)
    open_event = Any


    def traits_view(self):
        v = View(Item('container',
                         show_label=False, style='custom',
                         editor=ComponentEditor(),
                         ),
                 resizable=True,
                 width=self.window_width,
                 height=self.window_height,
                 )
        return v

class ProcessScript(DatabaseManager):
    _figure = None
    window = Any
    def run(self, p):
        txt = open(p, 'r').read()
        code = compile(txt, '<string>', 'exec')

        import ast
        import yaml
        m = ast.parse(txt)
        docstr = ast.get_docstring(m)
        self.parameters_dict = yaml.load(docstr)

        ctx = dict(sess=self.db.get_session(),
                   and_=and_,
                   ideogram=self._ideogram,
                   save=self._save,
                   group_by_labnumber=self._group_by_labnumber,
                   convert_records=self._convert_records,
                   )

        exec code in ctx
        ctx['main']()

#===============================================================================
# commands
#===============================================================================
    def _ideogram(self, analyses):

        wparams = self.parameters_dict['window']
        g = Window(
                   window_width=wparams['width'],
                   window_height=wparams['height'],
                   )
        self.window = g
        p = Ideogram()

        gideo = p.build(analyses)
        if gideo:
            gideo, plots = gideo
            self._figure = gideo
            g.container.add(gideo)
            g.edit_traits()


    def _save(self, p, figure=None):
        root = os.path.dirname(p)
        base = os.path.basename(p)
        base, ext = os.path.splitext(base)
        p, _c = unique_path(root, base, extension=ext)

        if figure is None:
            figure = self._figure

        if figure:

            gc = PdfPlotGraphicsContext(filename=p,
#                                      pdf_canvas=canvas,
#                                      dest_box=dest_box,
                                      pagesize='letter',
                                      dest_box_units='inch')

            comp = self._figure
            gc.render_component(comp, valign='center')
            gc.save()


    def _group_by_labnumber(self, ans):
        groups = dict()
        for ri in ans:
            if ri.labnumber in groups:
                group = groups[ri.labnumber]
                group.append(ri.labnumber)
            else:
                groups[ri.labnumber] = [ri.labnumber]

        keys = sorted(groups.keys())

        for ri in ans:
            ri.group_id = keys.index(ri.labnumber)

    def _convert_records(self, recs):
        return [Analysis(dbrecord=IsotopeRecord(_dbrecord=ri)) for ri in recs]

    def _test_fired(self):
        p = '/Users/ross/Sandbox/scripts/a.py'
        self.run(p)

    def traits_view(self):
        v = View(Item('test'))
        return v



if __name__ == '__main__':
    c = ProcessScript()
    c.db.connect()
    c.configure_traits()
#============= EOF =============================================
