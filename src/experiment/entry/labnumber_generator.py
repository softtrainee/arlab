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
from traits.api import Any, Float

#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable


class LabnumberGenerator(Loggable):
    db = Any
    default_j = Float(1e-4)
    default_j_err = Float(1e-7)

    def generate_labnumbers(self, irradiation):
        db = self.db
        ok = True
        #ok=self.confirmation_dialog('Are you sure you want to generate the labnumbers for this irradiation?')
        if ok:
            overwrite = False
            #overwrite=self.confirmation_dialog('Overwrite existing labnumbers?')
            with db.session_ctx():
                self._generate_labnumbers(irradiation, overwrite)


    def _generate_labnumbers(self, ir, overwrite=False, offset=0, level_offset=0):
        '''
            get last labnumber

            start numbering at 1+offset

            add level_offset between each level
        '''

        lngen = self._labnumber_generator(ir,
                                          overwrite,
                                          offset,
                                          level_offset
        )
        while 1:
            try:
                pos, ln = lngen.next()
            except StopIteration:
                break

            pos.labnumber.identifier = ln

            le = pos.level.name
            pi = pos.position
            self._add_default_flux(pos)
            self.info('setting irrad. pos. {} {}-{} labnumber={}'.format(ir, le, pi, ln))

    def _add_default_flux(self, pos):
        db = self.db
        j, j_err = self.default_j, self.default_j_err
        dbln = pos.labnumber

        def add_flux():
            hist = db.add_flux_history(pos)
            dbln.selected_flux_history = hist
            f = db.add_flux(j, j_err)
            f.history = hist

        if dbln.selected_flux_history:
            tol = 1e-10
            flux = dbln.selected_flux_history.flux
            if abs(flux.j - j) > tol or abs(flux.j_err - j_err) > tol:
                add_flux()
        else:
            add_flux()

    def _labnumber_generator(self, irradiation, overwrite, offset, level_offset):

        def gen(offset, level_offset):
            db = self.db
            last_ln = db.get_last_labnumber()
            if last_ln:
                last_ln = int(last_ln.identifier)
            else:
                last_ln = 0

            i = 0
            if not offset:
                last_ln += 1

            sln = last_ln + offset
            irrad = db.get_irradiation(irradiation)

            for level in irrad.levels:
                for position in level.positions:
                    if position.labnumber.identifier and not overwrite:
                        le = '{}{}-{}'.format(irrad.name, level.name, position.position)
                        ln = position.labnumber.identifier
                        self.warning('skipping position {} already has labnumber {}'.format(le, ln))
                        continue

                    yield position, sln + i
                    i += 1

                if level_offset:
                    sln = sln + level_offset
                    i = 0
                    if not offset:
                        i = -1


        return gen(offset, level_offset)

        #============= EOF =============================================

