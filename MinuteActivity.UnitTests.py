#!/usr/bin/python
import time
import unittest
from fRaspberryPIUtils import *
from MinuteActivity import *

# http://www.drdobbs.com/testing/unit-testing-with-python/240165163?pgno=2
# https://docs.python.org/2/library/unittest.html
 
class MinuteActivity_UnitTests(unittest.TestCase):

    def Trace(self, m):
        #print(m)
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructorAndIndividualProperties(self):
        ma = MinuteActivity("15.01.19 21:17")
        self.assertEqual(15, ma.Year)
        self.assertEqual(01, ma.Month)
        self.assertEqual(19, ma.Day)
        self.assertEqual(21, ma.Hour)
        self.assertEqual(17, ma.Minute)
        print("ma:"+str(ma))

    def testDecMinute(self):
        ma    = MinuteActivity("15.01.19 01:01")
        maDec = ma.DecMinute()
        self.assertEqual("15.01.19 01:00", maDec.MinuteId)
        maDec = maDec.DecMinute()
        self.assertEqual("15.01.19 00:59", maDec.MinuteId)

    def testGetFQNDay(self):
        ma = MinuteActivity("15.01.19 01:01")
        self.assertEqual("15.01.19", ma.GetFQNDay("15.01.19 01:01"))

    def testInitialize(self):
        ma1 = MinuteActivity("15.01.19 01:01")
        ma2 = MinuteActivity().Initialize(15, 01, 19, 01, 01)
        self.assertEqual(ma1.MinuteId, ma2.MinuteId)

if __name__ == "__main__":
    unittest.main()