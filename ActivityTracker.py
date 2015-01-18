import RPi.GPIO as GPIO
import time
#import fRaspberryPI *
from fRaspberryPI import * # Import al in the current namespace

######################################################################
## Main                                                             ##
######################################################################
mainLed         = Led(7)
motionSensor    = RadioShackPIRSensor(12)
timeOut         = TimeOut(250)

mainLed.SetBlinkMode(1000)
Board.Trace("Timeout:%s, time:%d" %(timeOut, millis()))

dailyActivity = {}

while True:
    mainLed.Blink()
    if(timeOut.IsTimeOut()):
        if(motionSensor.MotionDetected()):
            minuteId = StringFormat.GetLocalTimeStampMinute()
            if dailyActivity.has_key(minuteId):
                Board.Trace("Motion Detected - already recorded %s" % (minuteId))
            else:    
                dailyActivity[minuteId] = True
                Board.Trace("Motion Detected - %s" % (minuteId))
            mainLed.Blink(40, 100) # Blink for 4 seconds quickly
            Board.Trace("Ready")

Board.Done()
