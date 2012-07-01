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

#============= standard library imports ========================
import unittest
from threading import Thread
import time
#============= local library imports  ==========================
from src.testing.diode_tests import DiodeTests
from src.testing.extraction_line_tests import ExtractionLineTests
from src.testing.co2_tests import CO2Tests
import os
from src.paths import paths
from datetime import datetime

def write_results(results):
    p = os.path.join(paths.test_dir, 'output.txt')
    new_line = lambda x: '{}\n'.format(x)
    marker_line = lambda x: '#' + '=' * 39 + x + '=' * (40 - len(x))
    with open(p, 'w') as f:
        fwrite = lambda x: f.write(new_line(x))
        fwrite('#' + '=' * 79)
        fwrite('Automated Pychron Testing Results')
        fwrite('{}'.format(datetime.fromtimestamp(time.time())))
        fwrite('#' + '=' * 79)

        fwrite(marker_line('Errors'))
        for ei in results.errors:
            fwrite('------{}'.format(ei[0]))
            f.write(ei[1])
            fwrite('')

        fwrite(marker_line('Failures'))
        for ei in results.failures:
            fwrite('------{}'.format(ei[0]))
            f.write(ei[1])
            fwrite('')
        fwrite(marker_line('EOF'))

def run_tests(logger):
    def _run():
        time.sleep(0.1)
        logger.info('==========================================================')
        logger.info('=====================START TESTS=========================')
        logger.info('==========================================================')
        loader = unittest.TestLoader()

        #test cases executed in this order
        #tests executed in alphabetically order
        suites = [loader.loadTestsFromTestCase(t) for t in [
                                                            ExtractionLineTests,
                                                            DiodeTests,
                                                            CO2Tests
                                                            ]]

        suite = unittest.TestSuite(suites)
        runner = unittest.TextTestRunner()
        results = runner.run(suite)
        write_results(results)

    p = Thread(target=_run)
    p.start()

#============= EOF =============================================

