import time

######################################################################
##
class ComponentBaseObject(object):

    def __init__(self, debugOn = False):
        self.DebugOn = debugOn

    def Trace(self, m):
        mm = "[%s]%s" % (StringFormat.GetTime(), m)
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
        return time.strftime("%H:%M:%S", time.localtime(time.time()))

    def GetLocalTimeStamp(self):
        return time.strftime("%y.%m.%d %H:%M:%S", time.localtime(time.time()))

    def GetLocalTimeStampMinute(self):
        return time.strftime("%y.%m.%d %H:%M", time.localtime(time.time()))

# -- Declare global singleton --
StringFormat = StringFormatClass()
