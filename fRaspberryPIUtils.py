import time

######################################################################
##
class ComponentBaseObject(object):

    def __init__(self, pin = None, debugOn = False):
        self.DebugOn = debugOn
        self._pin    = pin

    def Trace(self, m):
        mm = "[%s]%s" % (StringFormat.GetTime(), m)
        print(mm)

    def Debug(self, m):
        if self.DebugOn:
            if self._pin == None:
                mm = "[%s][obj:%s] %s" % (StringFormat.GetTime(), self.__class__.__name__, m)
            else:
                mm = "[%s][obj:%s, pin:%d] %s" % (StringFormat.GetTime(), self.__class__.__name__, self._pin, m)
            print(mm)

######################################################################
## http://www.tutorialspoint.com/python/time_strftime.htm            
## http://www.tutorialspoint.com/python/python_date_time.htm
class StringFormatClass(ComponentBaseObject):

    def __init__(self):
        super(StringFormatClass, self).__init__()
        self.Debug("Init board")

    def GetTime(self):
        return time.strftime("%H:%M:%S", time.localtime(time.time()))

    def GetLocalTimeStamp(self):
        return time.strftime("%y.%m.%d %H:%M:%S", time.localtime(time.time()))

    def GetLocalTimeStampMinute(self):
        return time.strftime("%y.%m.%d %H:%M", time.localtime(time.time()))

# -- Declare global singleton --
StringFormat = StringFormatClass()
