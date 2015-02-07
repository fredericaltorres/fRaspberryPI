import time
import socket
import platform
import os
if platform.system() == 'Windows':
    pass
else:
    import fcntl # < This does not work on Windows
    import struct

######################################################################
##
class ComponentBaseObject(object):

    def __init__(self, pin = None, debugOn = False):
        self.DebugOn = debugOn
        self._pin    = pin

    def GetOsInfo(self):
        return "%s %s (%s)" % (platform.system(), platform.release(), os.name)

    def IsWindows(self):
        return platform.system() == 'Windows'

    def IsLinux(self):
        return platform.system() == 'Linux'

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

######################################################################
##
##
class NetworkUtilClass(ComponentBaseObject):

    def __init__(self):
        super(NetworkUtilClass, self).__init__()
        self.Debug("NetworkUtilClass")

    def __GetLocalIp(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

    def GetWifiIp(self):
        if self.IsWindows():
            return "0.0.0.0"
        try:
            return self.__GetLocalIp('wlan0') # WiFi address of WiFi adapter. NOT ETHERNET
        except IOError:
            try:
                return self.__GetLocalIp('eth0') # WiFi address of Ethernet cable. NOT ADAPTER
            except IOError:
                return None

# -- Declare global singleton --
NetworkUtil = NetworkUtilClass()
