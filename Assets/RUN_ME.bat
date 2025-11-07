@echo off
title Windows Error
color 1f
mode con cols=120 lines=30
call getCmdPid
call windowMode -pid %errorlevel% -mode maximized
mode con lines=1000 cols=1000
/max
cls
color 1f
echo.
echo A problem has been detected and Windows has been shut down to prevent damage
echo to your computer.
echo.
echo *** STOP: 0x0000007B (0xFFFFF880009A97E8,0xFFFFFFFFC0000034,0x0000000000000000,0x0000000000000000)
echo.
echo Collecting data for crash dump ...
echo Initializing disk for crash dump ...
echo Beginning dump of physical memory.
echo Dumping physical memory to disk: 100
echo Physical memory dump complete.
echo Contact your system administrator or technical support group for further assistance.

:: Wait 5 seconds before restarting
timeout /t 5 >nul

:: Restart safely (no admin required)
shutdown /r /t 0
