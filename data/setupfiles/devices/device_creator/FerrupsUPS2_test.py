
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