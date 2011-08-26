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

import unittest
from src.hardware.FerrupsUPS2 import FerrupsUPS2
class FerrupsUPS2Test(unittest.TestCase):
	def setUp(self):
		self.device=FerrupsUPS2()

	def test_get_status(self):
		r=self.device.get_status()
		self.assertEqual(r,None)

	def test_get_ambient_temperature(self):
		r=self.device.get_ambient_temperature()
		self.assertEqual(r,None)

	def test_get_temper(self):
		r=self.device.get_temper()
		self.assertEqual(r,None)

if __name__ == '__main__':
    unittest.main()