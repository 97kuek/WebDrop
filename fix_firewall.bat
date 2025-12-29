@echo off
powershell -Command "New-NetFirewallRule -DisplayName 'WebDrop P2P Transfer' -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow"
python -c "import socket; print(socket.gethostbyname(socket.gethostname()))"
echo Firewall rule added. Please restart WebDrop.
pause
