
import unittest
from src.hardware.FerrupsUPS import FerrupsUPS
class FerrupsUPSTest(unittest.TestCase):
	def setUp(self):
		self.device=FerrupsUPS()

	def test_get_status(self):
		r=self.device.get_status()
		self.assertEqual(r,None)

	def test_get_ambient_temperature(self):
		r=self.device.get_ambient_temperature()
		self.assertEqual(r,None)

if __name__ == '__main__':
    unittest.main()