@echo off
title WebDrop Server
echo Starting WebDrop...
echo Opening browser...
start http://localhost:8001
echo Server is running. Close this window to stop.
uvicorn server:app --host 0.0.0.0 --port 8001
pause
