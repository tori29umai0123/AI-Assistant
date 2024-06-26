[日本語](README.md) | [EN](README_en.md) | [中文](README_zh_CN.md)
# AI-Assistant
这是一个绘图辅助AI的GUI应用程序，集成 [stable-diffusion-webui-forge](https://github.com/lllyasviel/stable-diffusion-webui-forge/tree/main) 作为后端。
![01](https://github.com/tori29umai0123/AI-Assistant/assets/1675141/07ea96a5-d9d0-4b87-a8f6-ba41b4680f33)

# 启动方法
## exe文件
你可以直接双击exe文件来启动应用程序。

通过指定以下参数，你可以在启动时设定语言。
```
AI_Assistant.exe --lang=jp
AI_Assistant.exe --lang=en
AI_Assistant.exe --lang=zh_CN
```
通过添加更多参数，您可以为Stable Diffusion Web UI添加选项（适用于高级用户）。
默认情况下，如下所示：
AI_Assistant.exe --lang=ja --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --skip-torch-cuda-test

此外，通过添加以下参数，您可以显示扩展UI（目前，在i2i标签中可以加载LoRA）：
```
--exui
```
## 针对专家
通过运行以下类似的bat文件，您可以轻松指定参数。<br>
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

## 开发者
配置好构建设置后，请运行`python AI_Assistant.py`。

# 构建设置（开发者）
开发使用Python 3.10.x。
由于使用了webui-forge库，因此在构建时需要匹配版本并执行以下步骤：
1. 运行 AI_Assistant_install.ps1 进行安装。
2. 在安全软件设置中，将文件夹和可执行文件名添加到排除列表中。
示例：对于Windows Defender，前往 Windows 安全性 → 病毒与威胁防护 → 病毒与威胁防护设置 → 管理设置 → 排除。如下指定：
AI_Assistant.exe（进程）
C:\AI_Assistant（文件夹）

## 生成执行文件
运行 venv.cmd，然后输入以下命令：
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
copy AI_Assistant_lowVRAM.bat dist\AI_Assistant\AI_Assistant_lowVRAM.bat
```
