import time
import json
import os.path
import httplib
import urllib
import copy

from fRaspberryPIUtils import *
from MinuteActivity import *

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

    #def Trace(self, m):
    #    print(m)    
    #def Debug(self, m):
    #    pass

    def __init__(self, fileName = None, supportCloud = False):
        # a dictionary containing key:%y.%m.%d %H:%M value:true if activity was detected
        super(DailyActivity, self).__init__()
        self.DailyActivity = {}
        self.SupportCloud  = supportCloud
        self.fileName      = fileName
        if fileName:
            self.Load()
    
    def AddActivityToCloud(self, minuteId):
        '''
            https://docs.python.org/2/library/httplib.html
            http://frederictorresmvc2015.azurewebsites.net/api/ActivityTracker?action=get
            http://frederictorresmvc2015.azurewebsites.net/api/ActivityTracker?action=set&minuteId=15.01.19%2013:46
        '''
        if self.SupportCloud:
            conn = None
            try:
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
            except:
                print "Issue connecting to the cloud - MinuteId:%s" % minuteId
            finally:
                if conn != None:
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
        if self.fileName:
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

    def GetReportForDay(self, minuteIdDay):
        textReport  = ""
        refDay      = MinuteActivity(minuteIdDay)
        refDayId    = refDay.GetFQNDay(refDay) # YY.MM.DD
        keys        = self.GetKeys()
        index       = -1
        for k in keys:
            if k.startswith(refDayId):
                index = keys.index(k)
                break
        if index == -1:
            textReport = "%sActivity for day:%s not found" % ("\r\n", minuteIdDay)
        else:
            textReport       = "%sActivity for day:%s" % ("\r\n", minuteIdDay)
            minuteActivity   = 0
            minuteInactivity = 0

            for h in range(0, 24):
                for m in range(0, 60):
                    ma = MinuteActivity().Initialize(refDay.Year, refDay.Month, refDay.Day, h, m)
                    if self.WasActive(ma.MinuteId):
                        minuteActivity += 1
                    else:
                        minuteInactivity +=1
            textReport += "%s - Minute Of Activity In The Day %d" % ("\r\n", minuteActivity)
            textReport += "%s - Minute Of Inactivity In The Day %d" % ("\r\n", minuteInactivity)

        return textReport
    
    def GetMinuteOfInactivityFromNow(self, displayDetail = False, oneResult = False):
        '''
            return a list [0] MinuteOfInactivityCount as int, [1] Hours+MinuteOfInactivity as string [2] LastMinuteOfActivity
        '''
        inactivityMinuteCounter = 0
        ma = MinuteActivity(StringFormat.GetLocalTimeStampMinute())
        while True:
            if displayDetail: print("Process %s " % (ma))

            # if ma == None -> we reach the beginning of the day    
            if ma == None or self.WasActive(ma.MinuteId):

                if displayDetail: print("Activity Found")
                # Substract 1 to not count the current minute which may not be finished
                inactivityMinuteCounter    -= 1
                inactivityHour              = inactivityMinuteCounter / 60
                inactivityMinuteReminder    = inactivityMinuteCounter - (inactivityHour * 60)
                inactivityHourMinuteSummary = "%02d Hours, %02d Minutes" % (inactivityHour, inactivityMinuteReminder)
                if oneResult:
                    return inactivityMinuteCounter
                else:
                    tmpMinuteId = ma.MinuteId if ma != None else "reached-bod"
                    return inactivityMinuteCounter, inactivityHourMinuteSummary, tmpMinuteId
            else:
                if displayDetail: print("Activity Not Found Found for %s" %(ma.MinuteId))
                inactivityMinuteCounter += 1
                ma = ma.DecMinute()

if __name__ == "__main__":

    tpl = '    "14.12.11 %02d:%02d": 1,'
    for h in range(8, 12+1):
        for m in range(0, 59+1):
            print(tpl % (h, m))
    for h in range(13, 17+1):
        for m in range(0, 59+1):
            print(tpl % (h, m))