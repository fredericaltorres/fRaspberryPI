@echo off
cls
set PYEXE=d:\Python27\python.exe
echo fRaspberryPI UnitTests Suite
echo ============================

%PYEXE% fRaspberryPIUtils.UnitTests.py
%PYEXE% MinuteActivity.UnitTests.py
%PYEXE% DailyActivity.UnitTests.py