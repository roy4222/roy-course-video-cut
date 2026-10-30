@echo off
rem Windows wrapper: make_episode.cmd <episode_dir> [steps...] [--workers N] [--nvenc]
"%~dp0.venv\Scripts\python.exe" "%~dp0make_episode.py" %*
