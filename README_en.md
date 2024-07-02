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
AI_Assistant.bat
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --exui
```

AI_Assistant_lowVRAM.bat
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --unet-in-fp8-e4m3fn
```

## Developer
After configuring the build settings, please run `python AI_Assistant.py`.

# Build Settings（Developer）
Developed with Python 3.10.x.
Due to the use of the webui-forge library, the following steps are necessary during the build to match the version

1. Run AI_Assistant_install.ps1 to install.
2. In the settings of the security software, add the folder and executable name to the exclusion list.
Example: For Windows Defender, go to Windows Security → Virus & threat protection → Virus & threat protection settings → Manage settings → Exclusions. Specify like this:
AI_Assistant.exe (process)
C:\AI_Assistant (folder)

## Executable Generation
Run venv.cmd, then enter the following command:
```
pyinstaller "AI_Assistant.py" ^
--clean ^
--copy-metadata rich ^
--add-data "javascript;.\javascript" ^
--add-data "ldm_patched;.\ldm_patched" ^
--add-data "localizations;.\localizations" ^
--add-data "modules;.\modules" ^
--add-data "modules_forge;.\modules_forge" ^
--add-data "repositories;.\repositories" ^
--add-data "cache.json;." ^
--add-data "script.js;." ^
--add-data "ui-config.json;." ^
--add-data "config_states;.\config_states" ^
--add-data "configs;.\configs" ^
--add-data "extensions-builtin;.\extensions-builtin" ^
--add-data "html;.\html"

xcopy /E /I /Y venv\Lib\site-packages\xformers dist\AI_Assistant\_internal\xformers
xcopy /E /I /Y venv\Lib\site-packages\pytorch_lightning dist\AI_Assistant\_internal\pytorch_lightning
xcopy /E /I /Y venv\Lib\site-packages\lightning_fabric dist\AI_Assistant\_internal\lightning_fabric
xcopy /E /I /Y venv\Lib\site-packages\gradio dist\AI_Assistant\_internal\gradio
xcopy /E /I /Y venv\Lib\site-packages\gradio_client dist\AI_Assistant\_internal\gradio_client
xcopy /E /I /Y venv\Lib\site-packages\kornia dist\AI_Assistant\_internal\kornia
xcopy /E /I /Y venv\Lib\site-packages\open_clip dist\AI_Assistant\_internal\open_clip
xcopy /E /I /Y venv\Lib\site-packages\jsonmerge dist\AI_Assistant\_internal\jsonmerge
xcopy /E /I /Y venv\Lib\site-packages\torchdiffeq dist\AI_Assistant\_internal\torchdiffeq
xcopy /E /I /Y venv\Lib\site-packages\cleanfid dist\AI_Assistant\_internal\cleanfid
xcopy /E /I /Y venv\Lib\site-packages\clip dist\AI_Assistant\_internal\clip
xcopy /E /I /Y venv\Lib\site-packages\resize_right dist\AI_Assistant\_internal\resize_right
xcopy /E /I /Y venv\Lib\site-packages\diffusers dist\AI_Assistant\_internal\diffusers
xcopy /E /I /Y venv\Lib\site-packages\onnx dist\AI_Assistant\_internal\onnx
xcopy /E /I /Y venv\Lib\site-packages\onnxruntime dist\AI_Assistant\_internal\onnxruntime
xcopy /E /I /Y venv\Lib\site-packages\scipy dist\AI_Assistant\_internal\scipy
xcopy /E /I /Y config_states dist\AI_Assistant\config_states
xcopy /E /I /Y configs dist\AI_Assistant\configs
xcopy /E /I /Y embeddings dist\AI_Assistant\embeddings
xcopy /E /I /Y extensions-builtin dist\AI_Assistant\extensions-builtin
xcopy /E /I /Y html dist\AI_Assistant\html
xcopy /E /I /Y javascript dist\AI_Assistant\javascript
xcopy /E /I /Y ldm_patched dist\AI_Assistant\ldm_patched
xcopy /E /I /Y localizations dist\AI_Assistant\localizations
xcopy /E /I /Y modules dist\AI_Assistant\modules
xcopy /E /I /Y modules_forge dist\AI_Assistant\modules_forge
xcopy /E /I /Y repositories dist\AI_Assistant\repositories
xcopy /E /I /Y scripts dist\AI_Assistant\scripts
xcopy /E /I /Y languages dist\AI_Assistant\languages
copy script.js dist\AI_Assistant\script.js
copy AI_Assistant_model_DL.cmd dist\AI_Assistant\AI_Assistant_model_DL.cmd
copy AI_Assistant_ReadMe.txt dist\AI_Assistant\AI_Assistant_ReadMe.txt
copy AI_Assistant_exUI.bat dist\AI_Assistant\AI_Assistant_exUI.bat
```
