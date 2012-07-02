#===============================================================================
# Copyright 2011 Jake Ross
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



#=============enthought library imports=======================
import unittest
#============= standard library imports ========================
#============= local library imports  ==========================
from src.remote_hardware.remote_hardware_manager import RemoteHardwareManager
from src.remote_hardware.errors.error import ErrorCode


class baseTest(unittest.TestCase):
    protocol = None

    def _test(self, request_types, data, v):
        def success(rt):
            result = self.manager.process_server_request(rt, data)
            if isinstance(result, ErrorCode):
                result = repr(result)

            self.assertEqual(result, v)

        if isinstance(request_types, list):
            for rt in request_types:
                success(rt)
        else:
            success(request_types)

    def _test_suite(self, request_types, data, v):
        def success(rt, di, vi):
            result = self.manager.process_server_request(rt, di)
            if not isinstance(vi, (str, int, float)) and issubclass(vi, ErrorCode):
                func = self.assertIsInstance
            else:
                func = self.assertEqual
#            if isinstance(result, ErrorCode):
#                result = repr(result)
            func(result, vi)
#            self.assertEqual(result, vi)


        def error(rt, di, vi):
            def e(dii, vii):
                result = self.manager.process_server_request(rt, dii)
                self.assertIsInstance(result, vii)

            if isinstance(di, tuple):
                for dii, vii in zip(di, vi):
                    e(dii, vii)
            else:
                e(di, vi)

        def failure(rt, di, vi):
            pass
#            self.assertRaises(vi, self.manager.process_server_request, rt, di)

        if isinstance(request_types, list):
            for rt in request_types:
                success(rt, data[0], v[0])
                error(rt, data[1], v[1])
        else:
            success(request_types, data[0], v[0])
            try:
                error(request_types, data[1], v[1])
            except IndexError:
                pass
            #failure(request_types, data[1], v[1])

    def setUp(self):
        self.manager = RemoteHardwareManager()

        #verfiy that all commands in the protocol are tested
        p = self.protocol()

        test = [t[4:] for t in dir(self) if t.startswith('test')]
        defs = []
        for c in p.commands:
            if c not in test:
                print '{} not tested'.format(c)
                defs.append('''    def test{}(self):
        data='{}'
        v='OK'
        self._test(['Diode','CO2'],data,v)'''.format(c, c))

        for t in test:
            if t not in p.commands:
                print 'surpurfluous test: {}'.format(t)

        for d in defs:
            print d
        if defs:
            print '==============================='
#============= EOF =====================================
