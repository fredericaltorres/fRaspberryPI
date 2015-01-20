from fRaspberryPIUtils import *
import MinuteActivity
import time
import json
import os.path
import copy

class MinuteActivity(ComponentBaseObject):
    '''
        MinuteActivity
        Represent a minute of activity on which we can execute operation
        like DecMinute() which will return the MinuteId instance for the previous minute
    '''    

    def __init__(self, minuteId):
        self.MinuteId = minuteId
        self.Minute   = self.__GetMinute(minuteId)
        self.Hour     = self.__GetHour(minuteId)
        self.Day      = self.__GetDay(minuteId)
        self.Month    = self.__GetMonth(minuteId)
        self.Year     = self.__GetYear(minuteId)

    def __Clone(self):
        return copy.deepcopy(self)

    #  15.01.19 21:17
    #  15.01.19 00:00
    def __Reassemble(self):
        self.MinuteId = "%02d.%02d.%02d %02d:%02d" % (self.Year, self.Month, self.Day, self.Hour, self.Minute)        

    def DecMinute(self):
        newInstance = self.__Clone()
        if newInstance.Minute > 0:
            newInstance.Minute -= 1
        else:
            if newInstance.Hour > 0:
                newInstance.Minute = 59
                newInstance.Hour  -= 1
            else:
                return None # if we reach the beginning of the day, just abandon return None
        newInstance.__Reassemble()
        return newInstance

    #           11111
    #  01234567890123
    #  15.01.19 21:17
    def __GetMinute(self, minuteId):
        return int(self.MinuteId[12:14])

    def __GetHour(self, minuteId):
        return int(self.MinuteId[9:11])

    def __GetDay(self, minuteId):
        return int(self.MinuteId[6:8])

    def __GetMonth(self, minuteId):
        return int(self.MinuteId[3:5])

    def __GetYear(self, minuteId):
        return int(self.MinuteId[0:2])     

    def __str__(self):
        return "MinuteId:%s, Minute:%02d, Hour:%02d, Day:%02d, Month:%02d, Year:%02d" % (self.MinuteId, self.Minute, self.Hour, self.Day, self.Month, self.Year)

    def __repr__(self):
        return self.__str__()
