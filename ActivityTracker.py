from fRaspberryPIUtils import *
import RPi.GPIO as GPIO
from fRaspberryPI import * # Import al in the current namespace
import time
import json
import os.path
import httplib
import urllib
import copy

class MinuteActivity(ComponentBaseObject):
    '''
        MinuteActivity
        Represent a minute of activity on which we can execute operation
        like DecMinute() which will return the MinuteId instance for the previous minute
    '''    

    def __init__(self, minuteId):
        self.MinuteId = minuteId
        self.Minute   = self.__GetMinute(minuteId)
        self.Hour     = self.__GetHour(minuteId)
        self.Day      = self.__GetDay(minuteId)
        self.Month    = self.__GetMonth(minuteId)
        self.Year     = self.__GetYear(minuteId)

    def __Clone(self):
        return copy.deepcopy(self)

    #  15.01.19 21:17
    #  15.01.19 00:00
    def __Reassemble(self):
        self.MinuteId = "%02d.%02d.%02d %02d:%02d" % (self.Year, self.Month, self.Day, self.Hour, self.Minute)        

    def DecMinute(self):
        newInstance = self.__Clone()
        if newInstance.Minute > 0:
            newInstance.Minute -= 1
        else:
            if newInstance.Hour > 0:
                newInstance.Minute = 59
                newInstance.Hour  -= 1
            else:
                return None # if we reach the beginning of the day, just abandon return None
        newInstance.__Reassemble()
        return newInstance

    #           11111
    #  01234567890123
    #  15.01.19 21:17
    def __GetMinute(self, minuteId):
        return int(self.MinuteId[12:14])

    def __GetHour(self, minuteId):
        return int(self.MinuteId[9:11])

    def __GetDay(self, minuteId):
        return int(self.MinuteId[6:8])

    def __GetMonth(self, minuteId):
        return int(self.MinuteId[3:5])

    def __GetYear(self, minuteId):
        return int(self.MinuteId[0:2])     

    def __str__(self):
        return "MinuteId:%s, Minute:%02d, Hour:%02d, Day:%02d, Month:%02d, Year:%02d" % (self.MinuteId, self.Minute, self.Hour, self.Day, self.Month, self.Year)

    def __repr__(self):
        return self.__str__()

class DailyActivity(ComponentBaseObject):    
    '''
        DailyActivity
        Store in memory and on disk (json file), the minute of activity.
        Communicate to the cloud web api each minute of activity when detected.
        Allow to execute the following operation on the data
            - GetMinuteOfInactivityFromNow()
    '''
    CloudApiDomain = "frederictorresmvc2015.azurewebsites.net"
    CloudApiUrl    = "/api/ActivityTracker?action=set&minuteId={0}"

    def Trace(self, m):
        print(m)    
    def Debug(self, m):
        pass

    def __init__(self):
        # a dictionary containing key:%y.%m.%d %H:%M value:true if activity was detected
        #if super(DailyActivity, self).__init__()
        self.DailyActivity = {}
        self.fileName      = "DailyActivity.json"
        self.Load()
    
    def AddActivityToCloud(self, minuteId):
        '''
            https://docs.python.org/2/library/httplib.html
            http://frederictorresmvc2015.azurewebsites.net/api/ActivityTracker?action=get
            http://frederictorresmvc2015.azurewebsites.net/api/ActivityTracker?action=set&minuteId=15.01.19%2013:46
        '''
        conn            = httplib.HTTPConnection(DailyActivity.CloudApiDomain)
        minuteIdEncoded = urllib.quote(minuteId.encode("utf-8"))
        url             = DailyActivity.CloudApiUrl.format(minuteIdEncoded)
        self.Debug("cloud api domain:{0}, url:{1}".format(DailyActivity.CloudApiDomain, url))
        conn.request("GET", url)
        r1 = conn.getresponse()
        if r1.status == 200:
            self.Debug(r1.read())
            self.Trace("cloud call succeeded")
        else:
            self.Trace("cloud api:{0} failed status:{1}, reason:{2}".format(url, r1.status, r1.reason))
        conn.close()

    def AddActivity(self, minuteId):
        if self.WasActive(minuteId):
            #Board.Trace("Motion Detected - already recorded %s" % (minuteId))
            return False
        else:
            self.DailyActivity[minuteId] = 1
            self.Save()
            self.AddActivityToCloud(minuteId)
            return True

    def WasActive(self, minuteId):   
        return self.DailyActivity.has_key(minuteId)

    def Save(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.DailyActivity))

    def Load(self):
        self.DailyActivity = {}
        if os.path.isfile(self.fileName):
            with open(self.fileName, 'r') as f:
                js = f.read()
                self.DailyActivity = json.loads(js)

    def GetCount(self):
        return len(self.DailyActivity.keys())

    def GetKeys(self):
        keys = self.DailyActivity.keys()
        sorted(keys, reverse=True) # Ascending
        return keys
    
    def GetMinuteOfInactivityFromNow(self, displayDetail = False):
        '''
            return a list [0] MinuteOfInactivityCount as int, [1] Hours+MinuteOfInactivity as string [2] LastMinuteOfActivity
        '''
        inactivityMinuteCounter = 0
        ma = MinuteActivity(StringFormat.GetLocalTimeStampMinute())
        while True:
            if displayDetail: print("Process %s " % (ma))
            if(ma == None or self.WasActive(ma.MinuteId)):
                print("Activity Found")
                inactivityHour              = inactivityMinuteCounter / 60
                inactivityMinuteReminder    = inactivityMinuteCounter - (inactivityHour * 60)
                inactivityHourMinuteSummary = "%02d Hours, %02d Minutes" % (inactivityHour, inactivityMinuteReminder)
                return inactivityMinuteCounter, inactivityHourMinuteSummary, ma.MinuteId
            else:
                print("Activity Not Found Found for %s" %(ma.MinuteId))
                inactivityMinuteCounter += 1
                ma = ma.DecMinute()

'''
dailyActivity = DailyActivity()
print("Count %d" % (dailyActivity.GetCount()))
#print("Keys:")
#for k in dailyActivity.GetKeys(): print(k)
print("--------------------------------")
minuteOfInactivity, inactivityHourMinuteSummary, lastMinuteOfActivity = dailyActivity.GetMinuteOfInactivityFromNow()
print("minuteOfInactivity %d minute(s) - %s" %(minuteOfInactivity, inactivityHourMinuteSummary))
print("lastMinuteOfActivity %s" %(lastMinuteOfActivity))
quit()
#dailyActivity.AddActivityToCloud("15.01.19 14:34")
'''

######################################################################
## Main                                                             ##
######################################################################
mainLed         = Led(7)
motionSensor    = RadioShackPIRSensor(12)
timeOut         = TimeOut(250)
dailyActivity   = DailyActivity()

mainLed.SetBlinkMode(1000)
Board.Trace("Timeout:%s, time:%d" %(timeOut, millis()))
Board.Trace("Activity Tracker Start @ %s" % (StringFormat.GetLocalTimeStampMinute()))

while True:
    mainLed.Blink()
    if(timeOut.IsTimeOut()):
        if(motionSensor.MotionDetected()):
            minuteId = StringFormat.GetLocalTimeStampMinute()
            newMotionDetectedForCurrentMinute = dailyActivity.AddActivity(minuteId)
            if newMotionDetectedForCurrentMinute:
                Board.Trace("Motion Detected - %s" % (minuteId))
                mainLed.Blink(40, 100) # Blink for 4 seconds quickly
                Board.Trace("Ready")
            else:    
                mainLed.Blink(40, 100) # Blink for 4 seconds quickly

Board.Done()
