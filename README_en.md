[日本語](README.md) | [EN](README_en.md) | [中文](README_zh_CN.md)
# AI-Assistant
This is a GUI application for drawing assistance AI, which integrates the [stable-diffusion-webui-forge](https://github.com/lllyasviel/stable-diffusion-webui-forge/tree/main) as its backend.
![01](https://github.com/tori29umai0123/AI-Assistant/assets/1675141/07ea96a5-d9d0-4b87-a8f6-ba41b4680f33)

# Startup
## exe
You can start the application by double-clicking the exe file directly.

You can specify the language at startup by providing the following arguments.
```
AI_Assistant.exe --lang=jp
AI_Assistant.exe --lang=en
AI_Assistant.exe --lang=zh_CN
```
Additionally, by adding more arguments, you can add options for the Stable Diffusion Web UI (for advanced users).
By default, it is specified as follows:
AI_Assistant.exe --lang=ja --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --skip-torch-cuda-test

Furthermore, by adding the following arguments, you can display an extended UI (currently, you can load LoRA in the i2i tab)
```
--exui
```
## For those who are familiar
You can easily specify arguments by running a bat file like the following.<br>
AI_Assistant_exUI.bat
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --exui
```

For low VRAM, create a bat file like the following:
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --unet-in-fp8-e4m3fn
```

## Developer
After configuring the build settings, run `AI_Assistant.bat` or `.venv\Scripts\python.exe AI_Assistant.py`.

# Build Settings (Developer)
Developed with Python 3.10.x, uv, and CUDA 12.8.
Due to the use of the webui-forge library, the following steps are necessary during the build to match the version.

## Prerequisites
- [uv](https://docs.astral.sh/uv/) (install.ps1 will install it automatically if not present)
- [CUDA Toolkit 12.8](https://developer.nvidia.com/cuda-12-8-0-download-archive)

## Environment Setup
Run AI_Assistant_install.ps1 to install.

## Security Software Exclusion
In the settings of the security software, add the folder and executable name to the exclusion list.<br>
Example: For Windows Defender, go to Windows Security → Virus & threat protection → Virus & threat protection settings → Manage settings → Exclusions. Specify like this:<br>
AI_Assistant.exe (process)<br>
C:\AI_Assistant (folder)

## Executable Generation
Run build.cmd. PyInstaller build and file copying are performed automatically based on the spec file.
Build output is located in `dist\AI_Assistant\`.
