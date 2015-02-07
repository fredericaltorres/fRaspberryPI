#!/bin/bash
#
clear
echo  Executing fRaspberryPI Library Unit Tests
sudo python fRaspberryPIUtils.UnitTests.py
sudo python MinuteActivity.UnitTests.py
sudo python DailyActivity.UnitTests.py
