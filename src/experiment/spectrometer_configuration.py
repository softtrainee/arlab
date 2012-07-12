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
from traits.api import HasTraits, Int, Float
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import yaml
#============= local library imports  ==========================

class SpectrometerConfiguration(yaml.YAMLObject):
    yaml_tag = u'!SpecConfig'
#    delay_before_baseline = None
#    magnet_settling_time = None
#    ncounts = None
#    nbaseline_counts = None
#    reference_mass = None
#    baseline_mass = None
#    integration_time = None

    def __init__(self, ncounts):
        self.delay_before_baseline = 10
        self.magnet_settling_time = 1
        self.ncounts = ncounts
        self.nbaseline_counts = 120
        self.reference_mass = 39.962
        self.baseline_mass = 33.5
        self.integration_time = 1



#    def load(self, p):
#        with open(p, 'r') as f:
#            def constructor(loader, node):
#                v = loader.construct_scalar(node)
#                s = SpectrometerConfiguration()
#                for f, attr, vi in zip([int, ],
#                                    ['ncounts', ],
#                                   v.split('\n')
#                                   ):
#                    setattr(s, attr, f(vi))
#
#                return s
#            yaml.add_constructor(u'!spec_config', constructor)
#            return yaml.load(f)

#    def dump(self, p):
#        with open(p, 'w') as f:
#            def rep(dumper, data):

#                d = u'''{spec.ncounts}
#{spec.reference_mass}
#{spec.baseline_mass}
#{spec.integration_time}    
#'''.format(spec=data)
#                return dumper.represent_scalar(u'!spec_config', d)


#            yaml.add_representer(SpectrometerConfiguration,
#                                 rep
#                                 )
#            return yaml.dump(self)


from unittest import TestCase
class SpectrometerConfigTest(TestCase):
    def setUp(self):
        self.spec_config = SpectrometerConfiguration()
        self.path = '/Users/ross/Sandbox/scd.yaml'
    def testDump(self):
        print self.spec_config.dump(self.path)

#
#    def testLoad(self):
#        f = self.spec_config.load(self.path)
#        self.assertIsInstance(f, SpectrometerConfiguration)
#        self.assertEqual(f.ncounts, 200)

if __name__ == '__main__':
    d = SpectrometerConfiguration(20)
#    print yaml.dump(d)
#    print d.dump('/Users/ross/Sandbox/scd.yaml')
#    d.load()
    p = '/Users/ross/Sandbox/scd.yaml'
    print yaml.load(open(p, 'r'))


#============= EOF =============================================
