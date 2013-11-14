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
import os

#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.isotope_database_manager import IsotopeDatabaseManager
from src.helpers.iterfuncs import partition
from src.paths import paths


class BaseEasy(IsotopeDatabaseManager):
    def _make_root(self, ep):
        sdoc = ep.doc('setup')
        ep_root = sdoc['root']
        root = os.path.join(paths.processed_dir, ep_root)
        if not os.path.isdir(root):
            os.mkdir(root)
        return root

    def _save_fusion(self, editor, root, ident):
        pass

        #    p, _ = unique_path(root, '{}_fusion_{}'.format(ident, tag), extension='.pdf')

    #    editor.save_file(p, force_layout=True)

    def _make(self, projects, root,
              fusion_editor,
              spec_editor, tag):
        db = self.db
        with db.session_ctx():
            lns = [ln for proj in projects
                   for si in db.get_samples(project=proj)
                   for ln in si.labnumbers]

            n = len(lns) + sum([len(li.analyses) for li in lns])
            prog = self.open_progress(n)

            for li in lns:
                #make dir for labnumber
                ident = li.identifier
                ln_root = os.path.join(root, ident)
                if not os.path.isdir(ln_root):
                    os.mkdir(ln_root)

                prog.change_message('Making {} for {}'.format(tag, ident))

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
                fusion_editor.set_items(unks)
                #fusion_editor.unknowns = unks

                self._save_fusion(fusion_editor, ln_root, ident)

            prog.increment()
            try:
                prog.close()
            except AttributeError:
                #progress already closed
                pass

            self.info('easy make finished')

#============= EOF =============================================
