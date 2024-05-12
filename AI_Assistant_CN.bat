@echo off
setlocal

set "script_dir=%~dp0"

set "exe_path=%script_dir%AI_Assistant.exe"

set "lang=zh_CN"

"%exe_path%" --lang=%lang%

endlocal
