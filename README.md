AI-Assistant
stable-diffusion-webui-forge をバックエンドに組み込んだ、お絵描き補助AIのGUIアプリです。

ビルド設定（開発者向け）
①AI_Assistant_install.ps1を実行してインストール
②セキュリティーソフトの設定で、フォルダと実行ファイル名を除外リストに追加する。
例：Windows Defenderの場合、Windows セキュリティ→ウイルスと脅威の防止→ウイルスと脅威の防止の設定→設定の管理→除外
AI_Assistant.exe(プロセス)
C:\AI_Assistant（フォルダ）
のように指定する。
③venv.cmdを実行。
```
pyinstaller "E:\AI-Assistant\AI_Assistant.py" ^
--clean ^
--collect-data tkinterdnd2 ^
--add-data "E:\AI-Assistant\javascript;.\javascript" ^
--add-data "E:\AI-Assistant\ldm_patched;.\ldm_patched" ^
--add-data "E:\AI-Assistant\localizations;.\localizations" ^
--add-data "E:\AI-Assistant\modules;.\modules" ^
--add-data "E:\AI-Assistant\modules_forge;.\modules_forge" ^
--add-data "E:\AI-Assistant\repositories;.\repositories" ^
--add-data "E:\AI-Assistant\cache.json;." ^
--add-data "E:\AI-Assistant\script.js;." ^
--add-data "E:\AI-Assistant\ui-config.json;." ^
--add-data "E:\AI-Assistant\config_states;.\config_states" ^
--add-data "E:\AI-Assistant\configs;.\configs" ^
--add-data "E:\AI-Assistant\extensions-builtin;.\extensions-builtin" ^
--add-data "E:\AI-Assistant\html;.\html"
```
```
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
copy AI_Assistant_CN.bat dist\AI_Assistant\AI_Assistant_CN.bat
copy AI_Assistant_EN.bat dist\AI_Assistant\AI_Assistant_EN.bat
```
