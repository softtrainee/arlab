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

#============= standard library imports ========================
#============= local library imports  ==========================
import os
from src.database.isotope_database_manager import IsotopeDatabaseManager
from src.experiment.easy_parser import EasyParser
from src.helpers.filetools import unique_path
from src.helpers.iterfuncs import partition
from src.paths import paths
from src.processing.tasks.figures.editors.ideogram_editor import IdeogramEditor


class EasyFigures(IsotopeDatabaseManager):
    def make_figures(self):
        ep = EasyParser()
        doc = ep.doc('figures')

        #make a figure for each labnumber
        projects = doc['projects']

        ideo_editor = IdeogramEditor(processor=self)
        options = doc['options']
        ideo_editor.plotter_options_manager.set_plotter_options(options['ideogram'])

        db = self.db
        with db.session_ctx():
            lns = [ln for proj in projects
                   for si in db.get_samples(project=proj)
                   for ln in si.labnumbers]

            n = len(lns) + sum([len(li.analyses) for li in lns])
            prog = self.open_progress(n)

            #make root
            sdoc = ep.doc('setup')
            ep_root = sdoc['root']
            root = os.path.join(paths.processed_dir, ep_root)
            if not os.path.isdir(root):
                os.mkdir(root)

            for li in lns:
                #make dir for labnumber
                ident = li.identifier
                ln_root = os.path.join(root, ident)
                if not os.path.isdir(ln_root):
                    os.mkdir(ln_root)

                prog.change_message('Making figure for {}'.format(ident))

                #group by stepheat vs fusion
                pred = lambda x: bool(x.step)
                ans = sorted(li.analyses, key=pred)
                stepheat, fusion = partition(ans, pred)

                #print 'ss',stepheat
                #print 'sff',fusion

                apred = lambda x: x.aliquot
                stepheat = sorted(stepheat, key=apred)

                #for aq, ais in groupby(stepheat, key=apred):
                #    print 'step',aq, ais

                unks = self.make_analyses(fusion, progress=prog)
                ideo_editor.unknowns = unks

                p, _ = unique_path(ln_root, '{}_ideo'.format(ident), extension='.pdf')
                ideo_editor.save_file(p, force_layout=True)

            prog.increment()
            try:
                prog.close()
            except AttributeError:
                #progress already closed
                pass


#============= EOF =============================================
