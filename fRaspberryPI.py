import RPi.GPIO as GPIO
import time
import sys
from fRaspberryPIUtils import *

# like in the Arduino world
def millis():
    return time.time() * 1000

OFF          = False
ON           = True
  

######################################################################
##
class BoardClass(ComponentBaseObject):

    def __init__(self):
        super(BoardClass, self).__init__()
        self.Debug("Init board")
        GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
        
    def SetPinOut(self, pin):
        self.Debug("SetPinOut pin:%d" % (pin))
        GPIO.setup(pin, GPIO.OUT) # Setup GPIO Pin x to OUT

    def SetPinInput(self, pin):
        self.Debug("SetPinInput pin:%d" % (pin))
        GPIO.setup(pin, GPIO.IN) # Setup GPIO Pin x to OUT

    def TerminateApplication(self):
        Board.Trace("Terminating Application")
        GPIO.cleanup()
        sys.exit(0)

    def PinOnOff(self, pin, onOff):
        self.Debug("PinOnOff(%d) = %s" % (pin, onOff))
        GPIO.output(pin, onOff)

    def DigitalRead(self, pin):
        val = GPIO.input(pin)
        self.Debug("DigitalRead(%d) = %d" % (pin, val))
        return val

    # http://raspi.tv/2013/rpi-gpio-0-5-2a-now-has-software-pwm-how-to-use-it
    def PinPWM(self, pin, level):
        self.Debug("PinPWM(%d) = %s" % (pin, level))
        pass

    # Same as Arduino
    def Delay(self,  millisValue):
        self.Debug("Delay:%f" % (millisValue))
        time.sleep(millisValue/1000.0)
        
    def Wait(self, seconds):
        self.Debug("Wait:%f" % (seconds))
        time.sleep(seconds)

# -- Declare global singleton --
Board = BoardClass()

######################################################################
## http://www.tutorialspoint.com/python/python_date_time.htm
class TimeOut(ComponentBaseObject):

    def __init__(self, duration, autoReset = True):
        super(TimeOut, self).__init__(duration)
        self.Debug("Init duration:%d" % (duration))
        self._duration = duration
        self.Counter   = 0
        self.AutoReset = autoReset
        self.Reset()

    def Reset(self):
        self._time   = millis()
        self.Counter += 1

    def MustRunNow(self):        
        return self.IsTimeOut()

    def IsTimeOut(self):
        b = (millis() - self._time) > self._duration
        if b and self.AutoReset:
            self.Reset();
        return b

    def __str__(self):
        return "TimeOut counter:%d, duration:%d, time:%d" % (self.Counter, self._duration, self._time)
        
    def __repr__(self):
        return self.__str__()

######################################################################
##
class Led(ComponentBaseObject):

    def __init__(self, pin):
        super(Led, self).__init__(pin)
        self.Debug("Init pin:%d" % (pin))
        Board.SetPinOut(pin)
        self._pin  = pin
        self.State = False
        self._rate = 0

    def Blink(self, blinkCount = -1, waitTime = -1):
        if blinkCount == -1:
            self.__BlinkAsync()
        else:
            self.__BlinkSync(blinkCount, waitTime)

    def __BlinkSync(self, blinkCount, waitTime):
        for i in range(0, blinkCount):
            self.SetState(True)
            Board.Delay(waitTime)
            self.SetState(False)
            Board.Delay(waitTime)

    def __BlinkAsync(self):
        if (self._rate > 0 and self.GetBlinkDurationCycle() > self._rate):
            self.State           = not self.State
            self._blinkStartTime = millis();
            self.SetState(self.State);

    def SetBlinkMode(self, rate):
        if rate == OFF or rate == 0:
            self._rate = 0
            self.SetState(False)
        else:    
            self._rate           = rate
            self._blinkStartTime = millis()
            self.SetState(True)
        return self            

    def SetBlinkModeOff(self):
        self._rate = 0
        self.SetState(False)

    def GetBlinkDurationCycle(self):
        return millis() - self._blinkStartTime;

    def On(self):
        return self.SetState(ON)

    def Off(self):
        return self.SetState(OFF)        

    def SetState(self, onOff):
        Board.PinOnOff(self._pin,  onOff)
        self.State = onOff
        return self

    def SetLevel(self, level):
        Board.PinPWM(self._pin,  level)        
        return self

    def __str__(self):
        return "Led pin:%d, State:%r" % (self._pin, self.State)
        
    def __repr__(self):
        return self.__str__()

######################################################################
## SunFounderRelay
class SunFounderRelay(ComponentBaseObject):

    def __init__(self, pin):
        super(SunFounderRelay, self).__init__(pin)
        self.Debug("Init pin:%d" % (pin))
        Board.SetPinOut(pin)
        self._pin  = pin
        self.State = False

    def On(self):
        return self.SetState(ON)

    def Off(self):
        return self.SetState(OFF)         

    def SetState(self, onOff):
        Board.PinOnOff(self._pin,  not onOff) # << SunFounderRelay are reverse
        self.State = onOff
        return self

    def __str__(self):
        return "Relay pin:%d, State:%r" % (self._pin, self.State)
        
    def __repr__(self):
        return self.__str__()        

######################################################################
##
class RadioShackPIRSensor(ComponentBaseObject):

    def __init__(self, pin):
        super(RadioShackPIRSensor, self).__init__(pin)
        self.Debug("Init pin:%d" % (pin))
        Board.SetPinInput(pin)
        self._pin  = pin

    def MotionDetected(self):
        return Board.DigitalRead(self._pin) == 1


######################################################################
##
class PullUpButton(ComponentBaseObject):

    def __init__(self, pin):
        self.DebugOn = True
        super(PullUpButton, self).__init__(pin)
        self.Debug("Init pin:%d" % (pin))
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self._pin           = pin
        self._previousInput = 1

    def IsPressed(self):
        r     = False
        input = GPIO.input(self._pin)
        self.Debug("input:%d" % (input))
        if self._previousInput == 1 and input == 0: # << Remember it is a Pull Up button
            Board.Delay(25)
            input = GPIO.input(self._pin)
            r = (input == 0)
        self._previousInput = input
        return r