#!/usr/bin/python
import time
import unittest
from fRaspberryPIUtils import *
from MinuteActivity import *
from DailyActivity import *


# http://www.drdobbs.com/testing/unit-testing-with-python/240165163?pgno=2
# https://docs.python.org/2/library/unittest.html
 
class DailyActivity_UnitTests(unittest.TestCase):

    def Trace(self, m):
        #print(m)
        pass
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testConstructor(self):
        da = DailyActivity("DailyActivity.Test.2014.12.12.json")
        self.assertEqual(600, da.GetCount())

if __name__ == "__main__":
    unittest.main()