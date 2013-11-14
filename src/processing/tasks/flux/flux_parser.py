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
from collections import namedtuple
import csv
from traits.api import Str

#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable


Position = namedtuple('Position', 'hole_id,identifer, j, jerr')


class FluxParser(Loggable):
    path = Str

    def iterpositions(self):
        return self._iter_positions()


class XLSFluxParser(FluxParser):
    def _iter_positions(self):
        ps = []
        return ps


class CSVFluxParser(FluxParser):
    def _get_index(self, header, ks):
        if not isinstance(ks, (list, tuple)):
            ks = (tuple,)

        for k in ks:
            for ki in (k, k.upper(), k.lower(), k.capitalize(), k.replace('_', '')):
                try:
                    return header.index(ki)
                except IndexError:
                    pass

    def _iter_positions(self):
        with open(self.path, 'r') as fp:
            reader = csv.reader(fp)
            header = reader.next()

            hidx = self._get_index(header, 'hole')
            ididx = self._get_index(header, ('runid', 'labnumber', 'l#', 'identifier'))
            jidx = self._get_index(header, 'j')
            jeidx = self._get_index(header, 'j_err')

            for line in reader:
                if line:
                    yield Position(line[hidx],
                                   line[ididx],
                                   line[jidx], line[jeidx])


#=============EOF =============================================
