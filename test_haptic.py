""" Test module for haptic.py """
import unittest
import haptic
import multiprocessing

class TestFonctionUtile(unittest.TestCase):
    """ Utils functions tests """
    def test_extract(self):
        """ Test extract function """
        fifo = multiprocessing.Queue()
        size = 5
        fifoverif = bytearray(range(0,size))
        for i in range(0,size):
            fifo.put(bytes([i]))
        fifotest = haptic.extract(fifo,size)
        self.assertEqual(fifotest,fifoverif)
if __name__ == '__main__':
    unittest.main()
