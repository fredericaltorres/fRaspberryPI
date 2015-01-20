import time
import json
import os.path
import httplib
import urllib
import copy

from fRaspberryPIUtils import *
import MinuteActivity

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

    def __init__(self, fileName = "DailyActivity.json"):
        # a dictionary containing key:%y.%m.%d %H:%M value:true if activity was detected
        #if super(DailyActivity, self).__init__()
        self.DailyActivity = {}
        self.fileName      = fileName
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

if __name__ == "__main__":

    tpl = '    "14.12.11 %02d:%02d": 1,'
    for h in range(8, 12+1):
        for m in range(0, 59+1):
            print(tpl % (h, m))
    for h in range(13, 17+1):
        for m in range(0, 59+1):
            print(tpl % (h, m))