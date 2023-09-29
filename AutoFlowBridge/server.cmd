@echo off

set port=8001
python -m websockets ws://localhost:%port%/
