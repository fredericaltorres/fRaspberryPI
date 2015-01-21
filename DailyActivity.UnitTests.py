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
        da = DailyActivity("DailyActivity.Test.2014.12.11.json")
        self.assertEqual(600, da.GetCount())

    def testGetReportForDay(self):
        da          = DailyActivity("DailyActivity.Test.2014.12.11.json")
        minuteId    = "14.12.11 00:00"
        report      = da.GetReportForDay(minuteId)
        print("report:"+report)
        self.assertTrue("Day 600" in report)
        self.assertTrue("Day 840" in report)
        self.assertTrue("Activity for day:14.12.11 00:00" in report)

    def testGetMinuteOfInactivityFromNow(self):
        da      = DailyActivity()
        t       = time.localtime(time.time())
        hour    = t.tm_hour

        # Populate the previous hour
        for m in range(0, 60):
            ma = MinuteActivity().Initialize(t.tm_year, t.tm_mon, t.tm_mday, hour-1, m)
            da.AddActivity(ma.MinuteId)
            #print("Create Activity:%s" % ma.MinuteId)

        self.assertEqual(60, da.GetCount())            

        minuteOfInactivityCount, hoursMinuteOfInactivity, lastMinuteOfActivity = da.GetMinuteOfInactivityFromNow(displayDetail = not True)
        s = "minuteOfInactivityCount:%d, hoursMinuteOfInactivity:%s, lastMinuteOfActivity:%s" %(minuteOfInactivityCount, hoursMinuteOfInactivity, lastMinuteOfActivity)
        print(s)
        self.assertEqual(t.tm_min, minuteOfInactivityCount)

        minuteOfInactivityCount = da.GetMinuteOfInactivityFromNow(displayDetail = False, oneResult = True)
        self.assertEqual(t.tm_min, minuteOfInactivityCount)

if __name__ == "__main__":
    unittest.main()