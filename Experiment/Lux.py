#!/usr/bin/env python
 
import RPi.GPIO as GPIO, time, os
DEBUG = 1
GPIO.setmode(GPIO.BCM)
 
def RCtime (RCpin):
    reading = 0
    GPIO.setup(RCpin, GPIO.OUT)
    GPIO.output(RCpin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(RCpin, GPIO.IN)
    # This takes about 1 millisecond per loop cycle
    while (GPIO.input(RCpin) == GPIO.LOW):
        reading += 1
    return reading
 
def demo1():
    while True:
        print RCtime(18)     # Read RC timing using pin #18

class LightRange(object):

    def __init__(self, start, type):
        self.Start = start
        self.Type  = type

    def InRange(self, val):
        return val <= self.Start

    def __str__(self):
        return "[%d]%s" % (self.Start, self.Type)

    def __repr__(self):
        return self.__str__()        

class LightDetector(object):
    def __init__(self):
        self._ranges = []
        # Value must be add from small to large
        self._ranges.append(LightRange(   50,  "A lot of light"))
        self._ranges.append(LightRange(  500,  "Some light"))
        self._ranges.append(LightRange( 3500,  "Very little light"))
        self._ranges.append(LightRange(100000, "No light"))

    def GetLightType(self, val):
        for r in self._ranges:
            if r.InRange(val):
                return "%s - %d" % (r.Type, val)
        return "Unknown value:%d" % (val)

def demo2():
    ld = LightDetector()
    while True:                                     
        lightType = ld.GetLightType(RCtime(18))
        print lightType

demo2()
