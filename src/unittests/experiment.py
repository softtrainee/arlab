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
from traits.api import HasTraits
from traitsui.api import View, Item
import unittest
from src.experiment.experimentor import Experimentor
import os
from src.unittests.database import get_test_database
from src.experiment.tasks.experiment_editor import ExperimentEditor
from src.experiment.tasks.experiment_task import ExperimentEditorTask
#============= standard library imports ========================
#============= local library imports  ==========================

class ExperimentTest(unittest.TestCase):
    def setUp(self):
        self.experimentor = Experimentor(connect=False)
        self.experimentor.db = get_test_database().db
        self._experiment_file = './data/experiment.txt'

        self.exp_task = ExperimentEditorTask()

    def testFile(self):
        p = self._experiment_file
        self.assertTrue(os.path.isfile(p))

    def testOpen(self):
        qs = self._load_queues()
        self.assertEqual(len(qs), 1)

    def testNRuns(self):
        n = 10
        queue = self._load_queues()[0]
        self.assertEqual(len(queue.automated_runs), n)

    def testAliquots(self):
        queue = self._load_queues()[0]
#         aqs = (31, 31, 2, 32, 32, 200, 201, 3, 40, 41)
        aqs = (31, 31, 2, 32, 32, 200, 200, 3, 40, 41)
        for aq, an in zip(aqs, queue.automated_runs):
            self.assertEqual(an.aliquot, aq)

    def testSteps(self):
        queue = self._load_queues()[0]
#         sts = ('A', 'B', '', 'A', 'B', '', '', '', '')
        sts = ('A', 'B', '', 'A', 'B', 'A', 'B', '', '')
        for st, an in zip(sts, queue.automated_runs):
            self.assertEqual(an.step, st)
# # #
    def testSample(self):
        queue = self._load_queues()[0]
        samples = ('NM-779', 'NM-779', '', 'NM-779', 'NM-779', 'NM-779',
                   'NM-779', '', 'NM-791', 'NM-791'
                   )
        for sample, an in zip(samples, queue.automated_runs):
            self.assertEqual(an.sample, sample)
# # #
    def testIrradation(self):
        queue = self._load_queues()[0]
        irrads = ('NM-251H', 'NM-251H', '', 'NM-251H', 'NM-251H', 'NM-251H',
                  'NM-251H', '', 'NM-251H', 'NM-251H')
        for irrad, an in zip(irrads, queue.automated_runs):
            self.assertEqual(an.irradiation, irrad)

    def _load_queues(self):
        man = self.experimentor
        path = self._experiment_file
        with open(path, 'r') as fp:
            txt = fp.read()

            qtexts = self.exp_task._split_text(txt)
            qs = []
            for qi in qtexts:
                editor = ExperimentEditor(path=path)
                editor.new_queue(qi)
                qs.append(editor.queue)

        man.test_queues(qs)
        man.experiment_queues = qs
        man.update_info()
        man.path = path
        man.executor.reset()
        return qs
#============= EOF =============================================
