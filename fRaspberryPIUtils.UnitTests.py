#!/usr/bin/python
import time
import unittest
from fRaspberryPIUtils import *

# http://www.drdobbs.com/testing/unit-testing-with-python/240165163?pgno=2
# https://docs.python.org/2/library/unittest.html
 
class StringFormatClass_UnitTests(unittest.TestCase):
    """Unit tests StringFormatClass"""

    def Trace(self, m):
        #print(m)
        pass
     
    def setUp(self):
        pass
     
    def tearDown(self):
        pass
     
    def testGetTime(self):
        self.Trace(StringFormat.GetTime())
        self.assertTrue(len(StringFormat.GetTime()) == 8)

    def testGetLocalTimeStamp(self):
        self.Trace(StringFormat.GetLocalTimeStamp())
        self.assertTrue(len(StringFormat.GetLocalTimeStamp()) > 0)        

    def testGetLocalTimeStampMinute(self):
        self.Trace(StringFormat.GetLocalTimeStampMinute())
        self.assertTrue(len(StringFormat.GetLocalTimeStampMinute()) > 0)                


class NetworkUtilClass_UnitTests(unittest.TestCase):
    """Sample test case"""

    def Trace(self, m):
        print(m)
        pass
     
    def setUp(self):
        pass
     
    def tearDown(self):
        pass
     
    def testGetWifiIp(self):
        ip = NetworkUtil.GetWifiIp()
        self.Trace("LocalIp: %s" % ip)
        self.assertTrue(len(ip) > 0)


# creating a new test suite
#newSuite = unittest.TestSuite()
# adding a test case
#newSuite.addTest(unittest.makeSuite(fRaspberryPIUtils_UnitTests))        

if __name__ == "__main__":
    unittest.main()