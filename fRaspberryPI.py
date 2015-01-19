import RPi.GPIO as GPIO
import time

# like in the Arduino world
def millis():
    return time.time() * 1000

######################################################################
##
class ComponentBaseObject(object):

    def __init__(self, debugOn = False):
        self.DebugOn = debugOn

    def Trace(self, m):
        mm = "%s" % (m)
        print(mm)

    def Debug(self, m):
        if self.DebugOn:
            mm = "[obj:%s] %s" % (self.__class__.__name__, m)
            print(mm)

######################################################################
## http://www.tutorialspoint.com/python/time_strftime.htm            
## http://www.tutorialspoint.com/python/python_date_time.htm
class StringFormatClass(ComponentBaseObject):

    def __init__(self):
        super(StringFormatClass, self).__init__()
        self.Debug("Init board")

    def GetTime(self):
        localtime = time.localtime(time.time())
        t = time.mktime(localtime)
        return time.strftime("%H:%M:%S", time.gmtime(t))

    def GetLocalTimeStamp(self):
        localtime = time.localtime(time.time())
        t = time.mktime(localtime)
        return time.strftime("%m.%d.%y %H:%M:%S", time.gmtime(t))

    def GetLocalTimeStampMinute(self):
        localtime = time.localtime(time.time())
        t = time.mktime(localtime)
        return time.strftime("%y.%m.%d %H:%M", time.gmtime(t))

# -- Declare global singleton --
StringFormat = StringFormatClass()


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

    def Done(self):
        self.Debug("Done board")
        GPIO.cleanup()

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

    def __init__(self, duration):
        super(TimeOut, self).__init__()
        self.Debug("Init duration:%d" % (duration))
        self._duration = duration
        self.Counter   = 0
        self.Reset()

    def Reset(self):
        self._time   = millis()
        self.Counter += 1

    def IsTimeOut(self):
        b = (millis() - self._time) > self._duration
        if b:
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
        super(Led, self).__init__()
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
        if (self.GetBlinkDurationCycle() > self._rate):
            self.State           = not self.State
            self._blinkStartTime = millis();
            self.SetState(self.State);

    def SetBlinkMode(self, rate):
        self._rate           = rate
        self._blinkStartTime = millis()
        self.SetState(True)

    def SetBlinkModeOff(self):
        self._rate = 0
        self.SetState(False)

    def GetBlinkDurationCycle(self):
        return millis() - self._blinkStartTime;

    def SetState(self, onOff):
        Board.PinOnOff(self._pin,  onOff)
        self.State = onOff

    def SetLevel(self, level):
        Board.PinPWM(self._pin,  level)        

    def __str__(self):
        return "Led pin:%d, State:%r" % (self._pin, self.State)
        
    def __repr__(self):
        return self.__str__()

######################################################################
##
class RadioShackPIRSensor(ComponentBaseObject):

    def __init__(self, pin):
        super(RadioShackPIRSensor, self).__init__()
        self.Debug("Init pin:%d" % (pin))
        Board.SetPinInput(pin)
        self._pin  = pin

    def MotionDetected(self):
        return Board.DigitalRead(self._pin) == 1
