import sys
import unittest
from pyftdi.ftdi import Ftdi
from six import print_


class FtdiTestCase(unittest.TestCase):
    """FTDI driver test case"""

    def test_multiple_interface(self):
        # the following calls used to create issues (several interfaces from
        # the same device). The test expects an FTDI 2232H here
        ftdi1 = Ftdi()
        ftdi1.open(vendor=0x0403, product=0x6014, interface=0)
        import time
        for x in range(5):
            print_("If#1: ", hex(ftdi1.poll_modem_status()))
            time.sleep(0.500)
        ftdi1.close()


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(unittest.makeSuite(FtdiTestCase, 'test'))
    return suite_

if __name__ == '__main__':
    import doctest
    doctest.testmod(sys.modules[__name__])
    unittest.main(defaultTest='suite')