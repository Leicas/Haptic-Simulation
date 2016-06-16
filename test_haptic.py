import unittest
import haptic
import multiprocessing

class TestFonctionUtile(unittest.TestCase):
    def test_extract(self):
        fifo = multiprocessing.Queue()
        size = 5
        fifoverif = bytearray(range(0,size))
        for i in range(0,size):
            fifo.put(bytes([i]))
        fifotest = haptic.extract(fifo,size)
        self.assertEqual(fifotest,fifoverif)
if __name__ == '__main__':
    unittest.main()
