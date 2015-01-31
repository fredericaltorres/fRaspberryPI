'''

'''
import RPi.GPIO as GPIO
import time
import json
import os.path
import httplib
import urllib
import copy
import signal
import sys


from fRaspberryPIUtils  import *
from fRaspberryPI       import *
from MinuteActivity     import *
from DailyActivity      import *

SWITCH_PIN                          = 11 # White Wire  - GPIO 17
MAIN_LED_PIN                        = 16 # Yellow wire - GPIO 23
LIGHT_PIN                           = 18 # Green Wire  - GPIO 24
MOTION_SENSOR_PIN                   = 12 # Orange Wire - GPIO 18

MINUTE_OF_INACTIVITY_THRESHHOLD                   = 1         # After 5 minutes of inactivity, we sill shut the lights
MOTION_SENSOR_TASK_TIMEOUT                        = 1000 / 4  # 4 time a seconds
MOTION_SENSOR_RESET_TIME                          = 1000 * 4  # The motion sensor takes 4 seconds to reset
MOTION_SENSOR_RESET_TIMEOUT_AFTER_USER_SHUT_LIGHT = 1000 * 30 # 4 time a seconds
USER_INFO_TASK_TIMEOUT                            = 1000 * 60 # Show user information on screen every minutes

MAIN_LED_BLINK_RATE_NO_ACTIVITY     = 1000 # Alternate every 1 seconds

# TODO: get rid of these 2 global variables
lightOn                          = ON # always start by turnin on the light
lastMinuteIdOfInactivityDetected = "" # Contains the last minuteId of inactivity
lights                           = None

def TurnLights(onOff, message = None):
    if message == None:
        message = "Turn Lights %s" %('On' if onOff else 'Off')
    Board.Trace(message)
    lights.SetState(onOff)

def ShowUserInfo(dailyActivity):
    '''
        Display some status information. Called every 30 seconds
    '''
    minuteIdOfInactivity    = StringFormat.GetLocalTimeStampMinute()
    minuteOfInactivityCount = dailyActivity.GetMinuteOfInactivityFromNow(oneResult = True)
    Board.Trace("User Info:");
    Board.Trace("   Minute Of Activity Acquired:%d"   %(dailyActivity.GetCount()))
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
    global motionSensorResetTask

    if lightOn == OFF: # Turn light on if activity and light are off
        lightOn = ON
        TurnLights(lightOn)

    minuteId = StringFormat.GetLocalTimeStampMinute()

    if dailyActivity.AddActivity(minuteId): # if first motion detection for current minute
        Board.Trace("Motion Detected - %s" % (minuteId))
        mainLed.SetBlinkMode(OFF).On();        
    else:
        Board.Trace("Motion ReDetected - %s" % (minuteId))
        mainLed.SetBlinkMode(OFF).On();

    motionSensorResetTask = TimeOut(MOTION_SENSOR_RESET_TIME)
    return lightOn

def ResetLedBlinkRateToNormal():
    mainLed.SetBlinkMode(MAIN_LED_BLINK_RATE_NO_ACTIVITY)    

def TerminateApplication(signal, frame):    
    mainLed.Off()
    Board.TerminateApplication()

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, TerminateApplication)    

    switch                  = PullUpButton(SWITCH_PIN)
    lights                  = SunFounderRelay(LIGHT_PIN).Off()
    mainLed                 = Led(MAIN_LED_PIN).Off()
    motionSensor            = RadioShackPIRSensor(MOTION_SENSOR_PIN)
    motionSensorTask        = TimeOut(MOTION_SENSOR_TASK_TIMEOUT)
    motionSensorResetTask   = None # TimeOut
    userInfoTask            = TimeOut(USER_INFO_TASK_TIMEOUT)
    dailyActivity           = DailyActivity("DailyActivity.json", supportCloud = True)

    ResetLedBlinkRateToNormal()

    Board.Trace("\r\nActivity Tracker Start @ %s\r\n" % (StringFormat.GetLocalTimeStampMinute()))

    TurnLights(lightOn)
    ShowUserInfo(dailyActivity)

    while True:

        mainLed.Blink() # Signal normal activity

        if motionSensorTask.MustRunNow():
            if motionSensorResetTask != None:
                if motionSensorResetTask.MustRunNow():
                    ResetLedBlinkRateToNormal()
                    motionSensorResetTask = None
                    Board.Trace("Motion sensor ready")
            else:
                if motionSensor.MotionDetected():
                    lightOn = HandleMotionDetected(lightOn);

        if(userInfoTask.MustRunNow()):
            lightOn = HandlePeriodOfInactivity(lightOn)
            ShowUserInfo(dailyActivity)

        if switch.IsPressed():
            lightOn = not lightOn
            if lightOn:
                TurnLights(lightOn, "User turned lights on")
                motionSensorResetTask = None
            else:                
                # user shutdown the light manually, stop detected motion for 30 seconds
                motionSensorResetTask = TimeOut(MOTION_SENSOR_RESET_TIMEOUT_AFTER_USER_SHUT_LIGHT)
                Board.Trace("User turned lights off, motion monitoring suspended for %d seconds" % (MOTION_SENSOR_RESET_TIMEOUT_AFTER_USER_SHUT_LIGHT / 1000))
                TurnLights(lightOn)
                ResetLedBlinkRateToNormal()
            Board.Delay(150) # Avoid bouncing this way for now

    TerminateApplication()
