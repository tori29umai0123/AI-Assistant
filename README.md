[日本語](README.md) | [EN](README_en.md) | [中文](README_zh_CN.md)
# AI-Assistant
[stable-diffusion-webui-forge](https://github.com/lllyasviel/stable-diffusion-webui-forge/tree/main) をバックエンドに組み込んだ、お絵描き補助AIのGUIアプリです。
![01](https://github.com/tori29umai0123/AI-Assistant/assets/1675141/07ea96a5-d9d0-4b87-a8f6-ba41b4680f33)

# 起動方法
## exeファイル
exeファイルをそのままダブルクリックで起動できます。

以下の引数を指定することで、起動時の言語を指定できます。
```
AI_Assistant.exe --lang=jp
AI_Assistant.exe --lang=en
AI_Assistant.exe --lang=zh_CN
```
さらに引数を追加することで、Stable Diffusion Web UIに対するオプションを追加できます(上級者向け)
デフォルトではこのように指定されています。
AI_Assistant.exe --lang=ja --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --skip-torch-cuda-test

また、以下の引数を追加することで拡張UIを表示できます（現在、i2iタブでLoRAを読み込めるようになりました）
```
--exui
```
## わかっている人向け
以下のようなbatファイルを実行することで、引数を簡単に指定できます。<br>
AI_Assistant_exUI.bat
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --exui
```

低VRAMの場合は以下のようなbatファイルを作成してください。
```
@echo off
start /d "%~dp0" AI_Assistant.exe --nowebui --xformers --skip-python-version-check --skip-torch-cuda-test --unet-in-fp8-e4m3fn
```

## 開発者向け
ビルド設定を行った上で、`AI_Assistant.bat`を実行するか、`.venv\Scripts\python.exe AI_Assistant.py`を実行してください。

# ビルド設定（開発者向け）
Python 3.10.x、uv、CUDA 12.8で開発されています。
webui-forgeのライブラリを使用しているため、ビルド時にはバージョンを合わせた上で以下の手順が必要です。

## 前提条件
- [uv](https://docs.astral.sh/uv/) (未インストールの場合、install.ps1が自動でインストールします)
- [CUDA Toolkit 12.8](https://developer.nvidia.com/cuda-12-8-0-download-archive)

## 環境構築
AI_Assistant_install.ps1を実行してインストール

## セキュリティソフトの除外設定
セキュリティーソフトの設定で、フォルダと実行ファイル名を除外リストに追加する。<br>
例：Windows Defenderの場合、Windows セキュリティ→ウイルスと脅威の防止→ウイルスと脅威の防止の設定→設定の管理→除外<br>
AI_Assistant.exe(プロセス)<br>
C:\AI_Assistant（フォルダ）<br>
のように指定する。

## 実行ファイル生成
build.cmdを実行してください。specファイルに基づいてPyInstallerビルドとファイルコピーが自動で行われます。
ビルド成果物は`dist\AI_Assistant\`に出力されます。
