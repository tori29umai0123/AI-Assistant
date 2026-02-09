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
AI_Assistant_exUI.bat
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --exui
```

对于低显存，请创建如下bat文件：
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --unet-in-fp8-e4m3fn
```

## 开发者
配置好构建设置后，运行 `AI_Assistant.bat` 或 `.venv\Scripts\python.exe AI_Assistant.py`。

# 构建设置（开发者）
使用 Python 3.10.x、uv 和 CUDA 12.8 开发。
由于使用了webui-forge库，因此在构建时需要匹配版本并执行以下步骤。

## 前提条件
- [uv](https://docs.astral.sh/uv/)（如果未安装，install.ps1 会自动安装）
- [CUDA Toolkit 12.8](https://developer.nvidia.com/cuda-12-8-0-download-archive)

## 环境搭建
运行 AI_Assistant_install.ps1 进行安装。

## 安全软件排除设置
在安全软件设置中，将文件夹和可执行文件名添加到排除列表中。<br>
示例：对于Windows Defender，前往 Windows 安全性 → 病毒与威胁防护 → 病毒与威胁防护设置 → 管理设置 → 排除。如下指定：<br>
AI_Assistant.exe（进程）<br>
C:\AI_Assistant（文件夹）

## 生成执行文件
运行 build.cmd。基于spec文件自动执行PyInstaller构建和文件复制。
构建输出位于 `dist\AI_Assistant\`。
