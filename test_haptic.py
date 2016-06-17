""" Test module for haptic.py """
import unittest
import haptic

class TestFonctionUtile(unittest.TestCase):
    """ Utils functions tests """
    def test_force(self):
        """ Test setforce function """
        force = haptic.setforce()
        forcebis = haptic.setforce()
        self.assertEqual(force, forcebis)
if __name__ == '__main__':
    unittest.main()
