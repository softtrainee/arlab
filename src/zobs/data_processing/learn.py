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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from sklearn import svm
#============= local library imports  ==========================
from src.loggable import Loggable

class Learner(Loggable):
    pass


class GetterLearner(Learner):
    _classifier = None
    def learn(self, data, targets):
        kw = dict(gamma=0.001,
                C=100.
                )

        self._classifier = svm.SVC(**kw)
        self._classifier.fit(data, targets)

    def predict(self, v):
        return self._classifier.predict(v)

    def assemble_data(self):
        '''
            0=None; 1=GP50; 2=D50; 3=NP10
            
            0=cold; 1=hot
            
            0=obama; 1=jam
            
            0=sanidine; 1=groundmass
            
            gettering features
            index:  name
            0:    getter a 
            1:    duration a
            2:    hot_cold a
            
            3:    getter b 
            4:    duration b
            5:    hot_cold b
            
            6:    getter c
            7:    duration c
            8:    hot_cold c
            
            9:    spectrometer
            10:    material
            11:    mass

            12:    40Ar
            13:    39Ar
            14:    37Ar
            15:    36Ar
            
            #n50-nMax delta - diff in linear fit for first 50 and all pts
            16:    delta_40
            17:    delta_39
            18:    delta_37
            19:    delta_36
            
            12:    
            
        '''

        data = [
                [0, 120, 1, 1, 120, 0, 2, 120, 0, 0, 0.89, 0, 0.5],
                [0, 120, 1, 1, 120, 0, 2, 120, 0, 0, 0.89, 0, 0.5],
                [0, 120, 1, 1, 120, 0, 2, 120, 0, 0, 1.90, 0, 3.5],
                [0, 120, 1, 1, 120, 0, 2, 120, 0, 0, 1.01, 0, 2.5],
                ]
        targets = [0, 0, 0, 1]

        return data, targets

#===============================================================================
# testing ... move to separate file
#===============================================================================
import unittest
class GetterLearnerTest(unittest.TestCase):
    def setUp(self):
        self.learner = GetterLearner()

    def testPredict(self):
        from sklearn import datasets
        digits = datasets.load_digits()

        self.learner.learn(digits.data[:-1], digits.target[:-1])

        p = self.learner.predict(digits.data[-1])
        self.assertEqual(p, digits.target[-1])

    def testAssemble(self):
        d, t = self.learner.assemble_data()
        self.learner.learn(d[:-1], t[:-1])

        p = self.learner.predict(d[-1])
        self.assertEqual(p, t[-1])

#============= EOF =============================================
