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

#============= enthought library imports =======================
from traits.api import Instance, Button
from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================
import csv
import struct
import os
#from pylab import transpose
from numpy import loadtxt, array
#============= local library imports  ==========================
#from src.database.nmgrl_database_adapter import NMGRLDatabaseAdapter
#from src.loggable import Loggable
#from src.helpers.paths import data_dir
from src.data_processing.regression.ols import OLS
from src.loggable import Loggable
from src.database.adapters.massspec_database_adapter import MassSpecDatabaseAdapter

mkeys = ['l2 value', 'l1 value', 'ax value', 'h1 value', 'h2 value']

'''
following information is necessary


'''

RUN_TYPE_DICT = dict(Unknown=1, Air=2, Blank=5)
SAMPLE_DICT = dict(Air=2, Blank=1)
ISO_LABELS = dict(H1='Ar40', AX='Ar39', L1='Ar38', L2='Ar37', CDD='Ar36')

DEBUG = True

class MassSpecDatabaseImporter(Loggable):
    db = Instance(MassSpecDatabaseAdapter)
    test = Button
    def _test_fired(self):
        self.add_analysis('19999-01', 'Unknown')

    def traits_view(self):
        v = View(Item('test', show_label=False))
        return v

    def _db_default(self):
        db = MassSpecDatabaseAdapter(
                                     )
#        if db.connect():

        return db

    def add_analysis(self, rid, aliquot, irradpos, baselines, signals, keys,
                     regression_results):
        '''
            
        '''
        if rid.startswith('B'):
            runtype = 'Blank'
            irradpos = -1
        elif rid.startswith('A'):
            runtype = 'Air'
            irradpos = -2
        else:
            runtype = 'Unknown'

        db = self.db
        #=======================================================================
        # add analysis
        #=======================================================================
        analysis = db.add_analysis(rid,
                                   aliquot,
                                   irradpos,
                                   RUN_TYPE_DICT[runtype])
        #=======================================================================
        # add data reduction session
        #=======================================================================
        drs = db.add_data_reduction_session()
        #=======================================================================
        # add changeable items
        #=======================================================================

        item = db.add_changeable_items(analysis, drs, commit=True)
        analysis.ChangeableItemsID = item.ChangeableItemsID

        add_results = False
        isos = []
        for det, iso in keys:
            #===================================================================
            # isotopes
            #===================================================================
            iso = db.add_isotope(analysis, det, iso)

            if add_results:
                i = regression_results[det].coefficients[-1]
                ierr = regression_results[det].coefficient_errors[-1]
                db.add_isotope_result(iso, drs, i, ierr)
            isos.append(iso)

        for bi in baselines:
            #===================================================================
            # baselines
            #===================================================================
            tb, vb = zip(*bi)
            blob = self._build_timeblob(tb, vb)
            label = '{} Baseline'.format(det.upper())
            ncnts = len(tb)
            db.add_baseline(blob, label, ncnts)

        for iso, si in zip(isos, signals):
            #===================================================================
            # peak time
            #===================================================================
            tb, vb = zip(*si)
            blob = self._build_timeblob(tb, vb)
            db.add_peaktimeblob(blob, iso)

        db.commit()

    def _build_timeblob(self, t, v):
        '''
        '''
        blob = ''
        for ti, vi in zip(t, v):
            blob += struct.pack('>ff', float(vi), float(ti))
        return blob



if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup

    logging_setup('db_import')
    d = MassSpecDatabaseImporter()

    d.configure_traits()

#============= EOF ====================================
