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

RelayOn = False
RelayOff = True

def TurnLights(onOff):
    print("Turn Lights %s" %('On' if onOff else 'Off'))
    if onOff:
        light1.SetState(RelayOn)
        light2.SetState(RelayOn)
    else:        
        light1.SetState(RelayOff)
        light2.SetState(RelayOff)

lastMinuteIdOfInactivityDetected = "" # Contains the last minuteId of inactivity 
minuteOfInactivityThreshHold     = 2
lightOn                          = True # always start by turnin on the light

if __name__ == "__main__":

    light1          = Led(16).SetState(RelayOff)
    light2          = Led(18).SetState(RelayOff)
    mainLed         = Led(7)
    motionSensor    = RadioShackPIRSensor(12)
    timeOut         = TimeOut(250)
    dailyActivity   = DailyActivity("DailyActivity.json", supportCloud = True)

    mainLed.SetBlinkMode(1000)
    Board.Trace("Activity Tracker Start @ %s" % (StringFormat.GetLocalTimeStampMinute()))
    TurnLights(lightOn)

    while True:

        mainLed.Blink()
        if(timeOut.IsTimeOut()):

            # Motion Detection
            if(motionSensor.MotionDetected()):

                if lightOn == False: # Turn light on if no activity and light are on
                    lightOn = True
                    TurnLights(lightOn)

                minuteId = StringFormat.GetLocalTimeStampMinute()
                newMotionDetectedForCurrentMinute = dailyActivity.AddActivity(minuteId)
                if newMotionDetectedForCurrentMinute:
                    Board.Trace("Motion Detected - %s" % (minuteId))
                    mainLed.Blink(40, 100) # Blink for 4 seconds quickly
                    Board.Trace("Ready")
                else:    
                    mainLed.Blink(40, 100) # Blink for 4 seconds quickly

            # Period of inactivity
            minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
            minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
            if minuteOfInactivityCount > minuteOfInactivityThreshHold and lastMinuteIdOfInactivityDetected != minuteIdOfInactivity:
                lastMinuteIdOfInactivityDetected = minuteIdOfInactivity
                Board.Trace("Detected Inactivity")
                if lightOn: # Turn light off if no activity and light are on
                    lightOn = False
                    TurnLights(lightOn)

    Board.Done()
