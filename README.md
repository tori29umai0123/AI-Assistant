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

## 開発者向け
ビルド設定を行った上で、`python AI_Assistant.py`を実行してください。

# ビルド設定（開発者向け）
python 3.10.xで開発されています。
webui-forgeのライブラリを使用しているため、ビルド時にはバージョンを合わせた上で以下の手順が必要です。

①AI_Assistant_install.ps1を実行してインストール<br>
②セキュリティーソフトの設定で、フォルダと実行ファイル名を除外リストに追加する。<br>
例：Windows Defenderの場合、Windows セキュリティ→ウイルスと脅威の防止→ウイルスと脅威の防止の設定→設定の管理→除外<br>
AI_Assistant.exe(プロセス)<br>
C:\AI_Assistant（フォルダ）<br>
のように指定する。<br>

## 実行ファイル生成
venv.cmdを実行し、以下のコマンドを入力
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
