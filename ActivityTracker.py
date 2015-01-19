import RPi.GPIO as GPIO
import time
import json
import os.path
#import fRaspberryPI *
from fRaspberryPI import * # Import al in the current namespace

class DailyActivity(object):

    def __init__(self):
        # a dictionary containing key:%y.%m.%d %H:%M value:true if activity was detected
        self.DailyActivity = {}
        self.fileName      = "DailyActivity.pkl"
        self.Load()

    def AddActivity(self, minuteId):
        if self.DailyActivity.has_key(minuteId):
            Board.Trace("Motion Detected - already recorded %s" % (minuteId))
        else:    
            self.DailyActivity[minuteId] = True
            Board.Trace("Motion Detected - %s" % (minuteId))
            self.Save()

    def Save(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.DailyActivity))

    def Load(self):
        self.DailyActivity = {}
        if os.path.isfile(self.fileName):
            with open(self.fileName, 'r') as f:
                js = f.read()
                self.DailyActivity = json.load(js)

######################################################################
## Main                                                             ##
######################################################################
mainLed         = Led(7)
motionSensor    = RadioShackPIRSensor(12)
timeOut         = TimeOut(250)
dailyActivity   = DailyActivity()

mainLed.SetBlinkMode(1000)
Board.Trace("Timeout:%s, time:%d" %(timeOut, millis()))

while True:
    mainLed.Blink()
    if(timeOut.IsTimeOut()):
        if(motionSensor.MotionDetected()):
            dailyActivity.AddActivity(StringFormat.GetLocalTimeStampMinute())
            mainLed.Blink(40, 100) # Blink for 4 seconds quickly
            Board.Trace("Ready")

Board.Done()
