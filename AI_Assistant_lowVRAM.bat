@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --unet-in-fp8-e4m3fn
