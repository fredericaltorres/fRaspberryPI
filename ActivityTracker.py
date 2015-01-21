import RPi.GPIO as GPIO
import time
import json
import os.path
import httplib
import urllib
import copy

from fRaspberryPIUtils import *
from fRaspberryPI import * # Import al in the current namespace
from MinuteActivity import *
from DailyActivity import *

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

def TurnLights(onOff):
    print("Turn Lights %s" %('On' if True else 'Off'))

LastMinuteIdOfInactivityDetected = "" # Contains the last minuteId of inactivity 
MinuteOfInactivityThreshHold     = 2
LightOn                          = True # always start by turnin on the light

if __name__ == "__main__":
    ######################################################################
    ## Main                                                             ##
    ######################################################################
    mainLed         = Led(7)
    motionSensor    = RadioShackPIRSensor(12)
    timeOut         = TimeOut(250)
    dailyActivity   = DailyActivity("DailyActivity.json", supportCloud = True)

    mainLed.SetBlinkMode(1000)
    Board.Trace("Activity Tracker Start @ %s" % (StringFormat.GetLocalTimeStampMinute()))

    TurnLights(LightOn)

    while True:
        mainLed.Blink()
        if(timeOut.IsTimeOut()):

            if(motionSensor.MotionDetected()):
                if LightOn == False: # Turn light on if no activity and light are on
                    LightOn = True
                    TurnLights(LightOn)

                minuteId = StringFormat.GetLocalTimeStampMinute()
                newMotionDetectedForCurrentMinute = dailyActivity.AddActivity(minuteId)
                if newMotionDetectedForCurrentMinute:
                    Board.Trace("Motion Detected - %s" % (minuteId))
                    mainLed.Blink(40, 100) # Blink for 4 seconds quickly
                    Board.Trace("Ready")
                else:    
                    mainLed.Blink(40, 100) # Blink for 4 seconds quickly

            minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
            minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
            if minuteOfInactivityCount > MinuteOfInactivityThreshHold and LastMinuteIdOfInactivityDetected != minuteIdOfInactivity:
                LastMinuteIdOfInactivityDetected = minuteIdOfInactivity
                Board.Trace("Detected Inactivity")
                if LightOn: # Turn light off if no activity and light are on
                    LightOn = False
                    TurnLights(LightOn)

    Board.Done()
