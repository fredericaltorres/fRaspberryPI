'''

'''
import RPi.GPIO as GPIO
import time
import json
import os.path
import httplib
import urllib
import copy

from fRaspberryPIUtils  import *
from fRaspberryPI       import *
from MinuteActivity     import *
from DailyActivity      import *

MAIN_LED_PIN = 16
LIGHT_PIN    = 18
lightOn      = ON # always start by turnin on the light

lastMinuteIdOfInactivityDetected = "" # Contains the last minuteId of inactivity
minuteOfInactivityThreshHold = 3

def TurnLights(onOff):
    Board.Trace("Turn Lights %s" %('On' if onOff else 'Off'))
    light1.SetState(onOff)

def ShowUserInfo(dailyActivity):
    # Display some status information every 30 seconds
    minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
    minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
    Board.Trace("User Info:");
    Board.Trace("   Minute Of Inactivity:%d - [%s, %s]"   %(minuteOfInactivityCount, dailyActivity.GetNewestMinuteId(), dailyActivity.GetOldestMinuteId()))
    Board.Trace("");

def HandlePeriodOfInactivity():
    '''    
        Detect if the period of inactivity pass the threshhold, if yes shut the lights
    '''
    minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
    minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
    if minuteOfInactivityCount > minuteOfInactivityThreshHold and lastMinuteIdOfInactivityDetected != minuteIdOfInactivity:
        lastMinuteIdOfInactivityDetected = minuteIdOfInactivity
        Board.Trace("Detected Inactivity")
        if lightOn: # Turn light off if no activity and light are on
            lightOn = OFF
            TurnLights(lightOn)   

def HandleMotionDetected():
    '''    
        Detect if the period of inactivity pass the threshhold, if yes shut the lights
    '''
    global lightOn
    if lightOn == OFF: # Turn light on if activity and light are off
        lightOn = ON
        TurnLights(lightOn)

    minuteId = StringFormat.GetLocalTimeStampMinute()
    if dailyActivity.AddActivity(minuteId): # if first motion detecton for current minute
        Board.Trace("Motion Detected - %s" % (minuteId))
        mainLed.Blink(20, 100) # Blink for 4 seconds quickly
        Board.Trace("Ready")
    else:
        mainLed.Blink(20, 100) # Just signal motion detected, blink for 4 seconds quickly

if __name__ == "__main__":

    light1           = SunFounderRelay(LIGHT_PIN).SetState(OFF)
    mainLed          = Led(MAIN_LED_PIN).SetState(OFF)
    motionSensor     = RadioShackPIRSensor(12)
    motionSensorTask = TimeOut(250)
    userInfoTask     = TimeOut(30 * 1000)
    dailyActivity    = DailyActivity("DailyActivity.json", supportCloud = True)

    mainLed.SetBlinkMode(1000)
    Board.Trace("Activity Tracker Start @ %s" % (StringFormat.GetLocalTimeStampMinute()))
    TurnLights(lightOn)
    ShowUserInfo(dailyActivity)

    while True:

        mainLed.Blink() # Signal normal activity

        if(motionSensorTask.MustRunNow() and motionSensor.MotionDetected()):
            HandleMotionDetected();

        if(userInfoTask.MustRunNow()):
            HandlePeriodOfInactivity()
            ShowUserInfo(dailyActivity)

    Board.Done()
