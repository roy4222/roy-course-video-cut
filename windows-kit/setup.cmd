@echo off
rem Double-click or run: setup.cmd [-Cuda] [-NoModels]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
