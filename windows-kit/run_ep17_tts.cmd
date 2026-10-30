@echo off
setlocal
if defined ML_VIDEO_KIT (set "KIT=%ML_VIDEO_KIT%") else (set "KIT=%~dp0")
if "%KIT:~-1%"=="\" set "KIT=%KIT:~0,-1%"
cd /d "%KIT%"
echo START TTS %DATE% %TIME% > "%KIT%\episodes\ep17.tts.log"
call make_episode.cmd episodes\ep17 tts --tts-mode line --whisper-device cuda >> "%KIT%\episodes\ep17.tts.log" 2>&1
echo EXIT %ERRORLEVEL% END %DATE% %TIME% >> "%KIT%\episodes\ep17.tts.log"
