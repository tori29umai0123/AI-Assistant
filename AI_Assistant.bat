@echo off
setlocal

set "script_dir=%~dp0"

set "exe_path=%script_dir%AI_Assistant.exe"

REM 引数から言語とオーバーライドを取得
set "lang=%~1"
set "override=%~2"

REM デフォルトの言語を設定
if "%lang%"=="" (
    for /f "tokens=2 delims=[]" %%i in ('"echo.|set /p=|chcp"') do set "cp=%%i"
    if "%cp%"=="932" (
        set "lang=JA"
    ) else if "%cp%"=="936" (
        set "lang=CN"
    ) else if "%cp%"=="437" (
        set "lang=EN"
    ) else (
        set "lang=EN"
    )
)

"%exe_path%" --lang=%lang% %override%

endlocal