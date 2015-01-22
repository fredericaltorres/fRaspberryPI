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

MAIN_LED_PIN                        = 16
LIGHT_PIN                           = 18
MITION_SENSOR_PIN                   = 12

MINUTE_OF_INACTIVITY_THRESHHOLD     = 5 # After 5 minutes of inactivity, we sill shut the lights
MAIN_LED_NORMAL_BLINK_RATE          = 1000 # Alternate every 1 seconds
MOTION_SENSOR_TASK_TIMEOUT          = 1000 / 4 # 4 time a seconds
USER_INFO_TASK_TIMEOUT              = 1000 * 60 # Every minute

# TODO: get rid of these 2 global variables
lightOn                          = ON # always start by turnin on the light
lastMinuteIdOfInactivityDetected = "" # Contains the last minuteId of inactivity
lights                           = None 

def TurnLights(onOff):
    Board.Trace("Turn Lights %s" %('On' if onOff else 'Off'))
    lights.SetState(onOff)

def ShowUserInfo(dailyActivity):
    '''
        Display some status information. Called every 30 seconds
    '''
    minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
    minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
    Board.Trace("User Info:");
    Board.Trace("   Minute Of Inactivity:%d - [%s, %s]"   %(minuteOfInactivityCount, dailyActivity.GetNewestMinuteId(), dailyActivity.GetOldestMinuteId()))
    Board.Trace("");

def HandlePeriodOfInactivity(lightOn):
    '''    
        Detect if the period of inactivity pass the threshold, if yes shut the lights
    '''
    global lastMinuteIdOfInactivityDetected
    minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
    minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
    if minuteOfInactivityCount > MINUTE_OF_INACTIVITY_THRESHHOLD and lastMinuteIdOfInactivityDetected != minuteIdOfInactivity:
        lastMinuteIdOfInactivityDetected = minuteIdOfInactivity
        Board.Trace("Detected Inactivity")
        if lightOn: # Turn light off if no activity and light are on
            lightOn = OFF
            TurnLights(lightOn)   
    return lightOn            

def HandleMotionDetected(lightOn):
    '''    
        Execute action when a motion has been detected
    '''
    if lightOn == OFF: # Turn light on if activity and light are off
        lightOn = ON
        TurnLights(lightOn)

    minuteId = StringFormat.GetLocalTimeStampMinute()
    if dailyActivity.AddActivity(minuteId): # if first motion detection for current minute
        Board.Trace("Motion Detected - %s" % (minuteId))
        mainLed.Blink(20, 100) # Blink for 4 seconds quickly
        Board.Trace("Ready")
    else:
        mainLed.Blink(20, 100) # Just signal motion detected, blink for 4 seconds quickly
    return lightOn 

if __name__ == "__main__":

    lights           = SunFounderRelay(LIGHT_PIN).SetState(OFF)
    mainLed          = Led(MAIN_LED_PIN).SetState(OFF)
    motionSensor     = RadioShackPIRSensor(MITION_SENSOR_PIN)
    motionSensorTask = TimeOut(MOTION_SENSOR_TASK_TIMEOUT)
    userInfoTask     = TimeOut(USER_INFO_TASK_TIMEOUT)
    dailyActivity    = DailyActivity("DailyActivity.json", supportCloud = True)

    mainLed.SetBlinkMode(MAIN_LED_NORMAL_BLINK_RATE)

    Board.Trace("\r\nActivity Tracker Start @ %s\r\n" % (StringFormat.GetLocalTimeStampMinute()))

    TurnLights(lightOn)
    ShowUserInfo(dailyActivity)

    while True:

        mainLed.Blink() # Signal normal activity

        if(motionSensorTask.MustRunNow() and motionSensor.MotionDetected()):
            lightOn = HandleMotionDetected(lightOn);

        if(userInfoTask.MustRunNow()):
            lightOn = HandlePeriodOfInactivity(lightOn)
            ShowUserInfo(dailyActivity)

    Board.Done()
