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
from src.spectrometer.molecular_weights import MOLECULAR_WEIGHTS
import struct
import os
from src.paths import paths
from pyface.message_dialog import warning


def load_isotopedb_defaults(db):
    for name, mass in MOLECULAR_WEIGHTS.iteritems():
                    db.add_molecular_weight(name, mass)

    for at in ['blank_air',
               'blank_cocktail',
               'blank_unknown',
               'background', 'air', 'cocktail', 'unknown']:
#                           blank', 'air', 'cocktail', 'background', 'unknown']:
        db.add_analysis_type(at)

    for mi in ['obama', 'jan', 'nmgrl map']:
        db.add_mass_spectrometer(mi)

    for i, di in enumerate(['blank_air',
               'blank_cocktail',
               'blank_unknown',
               'background', 'air', 'cocktail']):
        samp = db.add_sample(di)
        db.add_labnumber(i + 1, sample=samp)

    for hi, kind, make in [('Fusions CO2', '10.6um co2', 'photon machines'),
                          ('Fusions Diode', '810nm diode', 'photon machines'),
                          ('Fusions UV', '193nm eximer', 'photon machines')
                          ]:
        db.add_extraction_device(name=hi,
                                 kind=kind,
                                 make=make
                                 )


    mdir = os.path.join(paths.setup_dir, 'irradiation_tray_maps')
    if not os.path.isdir(mdir):
        warning(None, 'No irradiation_tray_maps directory. add to .../setupfiles')

    else:
        for t in os.listdir(mdir):
            if t.startswith('.'):
                continue
            p = os.path.join(mdir, t)
            if not os.path.isfile(p):
                continue

            with open(p, 'r') as f:
                h = f.readline()
                nholes, _diam = h.split(',')
                nholes = int(nholes)
                holes = [map(float, l.strip().split(',')) for i, l in enumerate(f) if i < nholes]
                blob = ''.join([struct.pack('>ff', x, y) for x, y in holes])
                db.add_irradiation_holder(t, geometry=blob)
    db.commit()

