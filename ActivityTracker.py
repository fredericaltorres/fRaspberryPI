import RPi.GPIO as GPIO
import time
import json
import os.path
from fRaspberryPI import * # Import al in the current namespace
import httplib
import urllib

class DailyActivity(ComponentBaseObject):

    #CloudApiDomain = "frederictorresmvc2015.azurewebsites.net"
    CloudApiDomain = "frederictorresmvc2015.azurewebsites.net"
    CloudApiUrl    = "/api/ActivityTracker?action=set&minuteId={0}"

    #def Trace(self, m):
    #    print(m)    
    #def Debug(self, m):
    #    pass

    def __init__(self):
        # a dictionary containing key:%y.%m.%d %H:%M value:true if activity was detected
        super(DailyActivity, self).__init__()
        self.DailyActivity = {}
        self.fileName      = "DailyActivity.json"
        self.Load()

    # https://docs.python.org/2/library/httplib.html
    # http://frederictorresmvc2015.azurewebsites.net/api/ActivityTracker?action=get
    # http://frederictorresmvc2015.azurewebsites.net/api/ActivityTracker?action=set&minuteId=15.01.19%2013:46
    def AddActivityToCloud(self, minuteId):
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
        if self.DailyActivity.has_key(minuteId):
            #Board.Trace("Motion Detected - already recorded %s" % (minuteId))
            return False
        else:
            self.DailyActivity[minuteId] = 1
            self.Save()
            self.AddActivityToCloud(minuteId)
            return True

    def Save(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.DailyActivity))

    def Load(self):
        self.DailyActivity = {}
        if os.path.isfile(self.fileName):
            with open(self.fileName, 'r') as f:
                js = f.read()
                self.DailyActivity = json.loads(js)

#dailyActivity = DailyActivity()
#dailyActivity.AddActivityToCloud("15.01.19 14:34")
#quit()

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
