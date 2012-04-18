'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from src.hardware.core.core_device import CoreDevice


class QtegraDevice(CoreDevice):
    scan_func = 'read_temperature'

    def _build_command(self, cmd, *args, **kw):
        return cmd

    def _parse_response(self, resp):
        if resp is not None:
            resp = resp.strip()
        return resp

    def read_temperature(self, **kw):
        cmd = 'Get {}'.format('Temp1')
        x = self.repeat_command(cmd, **kw)
        return x



