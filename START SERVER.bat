@echo off
title Launching Norm AI Components

start "youface" cmd /k "python youface.py"

start "Norm Server" cmd /k "python N0rm_Server.py"

start "Norm DB Listener" cmd /k "python N0rm_DB_listener.py"

echo Both Norm components launched.
pause