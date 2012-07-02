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
from datetime import datetime
import os
#============= local library imports  ==========================
from laser_tests import DiodeTests, CO2Tests
from extraction_line_tests import ExtractionLineTests
from remote_extraction_line_tests import RemoteExtractionLineTests
from remote_laser_tests import RemoteDiodeTests, RemoteCO2Tests

from src.paths import paths
def new_line(x):
    return '{}\n'.format(x)

def fwriter(f):
    return lambda x:f.write(new_line(x))

def marker_line(x):
    return '#' + '=' * 39 + x + '=' * (40 - len(x))

def write_results(results, title, names):
    p = os.path.join(paths.test_dir, 'output.txt')
    with open(p, 'w') as f:
        fwrite = fwriter(f)
        fwrite('#' + '=' * 79)
        fwrite('Automated Pychron Testing Results')
        fwrite('{}'.format(datetime.fromtimestamp(time.time())))
        fwrite('#' + '=' * 79)
        _write_results(f, results, title, names)

def finish_write_results():
    p = os.path.join(paths.test_dir, 'output.txt')
    with open(p, 'a') as f:
        fwrite = fwriter(f)
        fwrite(marker_line('EOF'))

def append_results(r, title, names):
    p = os.path.join(paths.test_dir, 'output.txt')
    with open(p, 'a') as f:
        _write_results(f, r, title, names)

def _write_results(f, results, title, names):
    fwrite = fwriter(f)
    fwrite('')
    fwrite(marker_line(title))
    fwrite('Number Tests={}'.format(results.testsRun))
    fwrite('Errors= {}'.format(len(results.errors)))
    fwrite('Failures= {}'.format(len(results.failures)))
    fwrite('Executed Tests')
    errornames = [ei._testMethodName for ei, _tb in results.errors]
    failnames = [ei._testMethodName for ei, _tb in results.failures]

    for ni in names:
        state = 'Error' if ni in errornames else 'Fail' if ni in failnames else 'Pass'
        fwrite('\t{:<40s} ={}'.format(ni, state))

    fwrite(marker_line('Errors'))
    for ei, tb in results.errors:
        fwrite('------ {}'.format(ei))
        f.write(tb)
        fwrite('')

    fwrite(marker_line('Failures'))
    for fi, tb in results.failures:
        fwrite('------ {}'.format(fi))
        fwrite(tb)
        fwrite('')

    fwrite('')

def run_tests(logger):
    def _run():
        time.sleep(3)
        logger.info('=====================TESTS================================')
        logger.info('==========================================================')
        logger.info('=====================Unit Tests===========================')

        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner()

        #test cases executed in this order
        #tests executed in alphabetically order
        utests = [
                ExtractionLineTests,
#               DiodeTests,
#                CO2Tests
                ]
        _execute_tests(logger,
                       loader, runner, utests, write_results, 'Unit')

        rtests = [
                  RemoteExtractionLineTests,
                  RemoteDiodeTests,
#                  RemoteCO2Tests
                  ]

        _execute_tests(logger,
                       loader, runner, rtests, append_results, 'Remote')

#        mrtests = []
#        _execute_tests(logger,
#                       loader, runner, mrtests, append_results, 'Mult Runs')

        finish_write_results()

    p = Thread(target=_run)
    p.start()

def _execute_tests(logger, loader, runner, tests, writefunc, title):
    logger.info('====== {} Tests ======'.format(title))

    suites = [loader.loadTestsFromTestCase(t) for t in tests]

    suite = unittest.TestSuite(suites)
    results = runner.run(suite)

    testnames = []
    map(testnames.extend, [loader.getTestCaseNames(t) for t in tests])
    writefunc(results, title, testnames)

#============= EOF =============================================

