@echo off
REM Kit folder = this script's folder, unless ML_VIDEO_KIT is set.
setlocal
if defined ML_VIDEO_KIT (set "KIT=%ML_VIDEO_KIT%") else (set "KIT=%~dp0")
if "%KIT:~-1%"=="\" set "KIT=%KIT:~0,-1%"
cd /d "%KIT%"
echo START %DATE% %TIME% > "%KIT%\episodes\%1.run.log"
call make_episode.cmd episodes\%1 tts timeline layout render mix mux master srt md qc yt --nvenc --whisper-device cuda >> "%KIT%\episodes\%1.run.log" 2>&1
echo EXIT %ERRORLEVEL% END %DATE% %TIME% >> "%KIT%\episodes\%1.run.log"
