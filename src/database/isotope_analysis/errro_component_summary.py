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
from src.database.isotope_analysis.summary import Summary

class ErrorComponentSummary(Summary):
    def _build_summary(self, *args, **kw):
        record = self.record

        keys = record.isotope_keys
        keys += ('j', 'ic_factor')
        vs = []
        mx = -1e20
        for key in keys:
            v = self.record.get_error_component(key)
            vs.append(v)
            if v > mx:
                max_key = key
                mx = v
        for key, v in zip(keys, vs):
            if key == max_key:
                self._print_value(key, v, int(v / 100.*50), color='red')
            else:
                self._print_value(key, v, int(v / 100.*50))

    def _print_value(self, key, value, magnitude, **kw):
        fmt = '{:<15s}= {:<10s}|{}'.format(key, self.floatfmt(value, n=3), '*' * magnitude)
        disp = self.display
        disp.add_text(fmt, **kw)

#============= EOF =============================================
