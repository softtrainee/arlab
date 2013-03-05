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
from traits.api import Any
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable


class Exporter(Loggable):
    figure = Any
    def export(self, path=None):
        if path is None:
            path = self._get_file_path()
        self.info('exporting to {}'.format(path))
        self._export(path)

    def _export(self, p):
        raise NotImplementedError

    @property
    def header(self):
        header = ['RID', 'DATE', 'TIME', 'TYPE', 'SAMPLE', 'IRRAD',
                  'AR40', 'AR40ERR',
                  'AR39', 'AR39ERR',
                  'AR38', 'AR38ERR',
                  'AR37', 'AR37ERR',
                  'AR36', 'AR36ERR',
                  'AR40bs', 'AR40bsERR',
                  'AR39bs', 'AR39bsERR',
                  'AR38bs', 'AR38bsERR',
                  'AR37bs', 'AR37bsERR',
                  'AR36bs', 'AR36bsERR',
                  'AR40bl', 'AR40blERR',
                  'AR39bl', 'AR39blERR',
                  'AR38bl', 'AR38blERR',
                  'AR37bl', 'AR37blERR',
                  'AR36bl', 'AR36blERR',
                  'AR40bg', 'AR40bgERR',
                  'AR39bg', 'AR39bgERR',
                  'AR38bg', 'AR38bgERR',
                  'AR37bg', 'AR37bgERR',
                  'AR36bg', 'AR36bgERR',
                  ]
        return header

    def _make_raw_row(self, ai):
        row = [ai.rid, ai.rundate, ai.runtime, ai.analysis_type, ai.sample, ai.irradiation]

#            dd = map(lambda s:map(lambda ki: s[0].endswith(ki), ks), ai.signals.iteritems())
#            for di in dd
#                sd = sum(di) > 0
#            ids=[]
        ks = ['bs', 'bl', 'bg']
        def exclude(kk):
            return sum(map(lambda ki: kk.endswith(ki), ks)) > 0

        signals = [v for k, v in ai.signals.iteritems() if not exclude(k)]
        row += [vv
               for v in signals
                for vv in (v.value, v.error)
                ]

        for ki in ks:
            signals = [v for k, v in ai.signals.iteritems() if k.endswith(ki)]
            row += [vv
                   for v in signals
                    for vv in (v.value, v.error)
                    ]
        return row
#============= EOF =============================================
