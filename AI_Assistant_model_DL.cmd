@echo off
REM 改行コードをWindows形式に変更
setlocal enabledelayedexpansion

REM モデルディレクトリの基本パスを実行ディレクトリのmodelsサブディレクトリに設定
set "dpath=%~dp0models"

REM Taggerモデルダウンロード
set "MODEL_DIR=%dpath%\tagger"
set "MODEL_ID=SmilingWolf/wd-swinv2-tagger-v3"
set "FILES=config.json model.onnx selected_tags.csv sw_jax_cv_config.json"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)


REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=2vXpSwA7/iroiro-lora"
set "FILES=sdxl-testlora-normalmap_04b_dim32.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/test3/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)


REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=tori29umai/lineart"
set "FILES=sdxl_BW_bold_Line.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)


REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=tori29umai/lineart"
set "FILES=sdxl_BWLine.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=tori29umai/SDXL_shadow"
set "FILES=anime01.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=tori29umai/SDXL_shadow"
set "FILES=anime02.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=tori29umai/SDXL_shadow"
set "FILES=anime03.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

REM Loraモデルダウンロード
set "MODEL_DIR=%dpath%\Lora"
set "MODEL_ID=tori29umai/flat_color"
set "FILES=SDXL_baketu2.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)




REM ControlNetモデルダウンロード
set "MODEL_DIR=%dpath%\ControlNet"
set "MODEL_ID=2vXpSwA7/iroiro-lora"
set "FILES=CN-anytest_v3-50000_am_dim256.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/test_controlnet2/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

REM ControlNetモデルダウンロード
set "MODEL_DIR=%dpath%\ControlNet"
set "MODEL_ID=2vXpSwA7/iroiro-lora"
set "FILES=CN-anytest_v4-marged_am_dim256.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/test_controlnet2/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)


REM ControlNetモデルダウンロード
set "MODEL_DIR=%dpath%\ControlNet"
set "MODEL_ID=stabilityai/control-lora"
set "FILES=control-lora-canny-rank256.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/control-LoRAs-rank256/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)



REM ControlNetモデルダウンロード
set "MODEL_DIR=%dpath%\ControlNet"
set "MODEL_ID=kataragi/ControlNet-LineartXL"
set "FILES=Kataragi_lineartXL-lora128.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)


REM civitaiからControlNetモデルダウンロード
set "MODEL_DIR=%dpath%\ControlNet"
set "DOWNLOAD_URL=https://civitai.com/api/download/models/506961?type=Model&format=SafeTensor"
set "FILES=controlnet852A_veryhard.safetensors"
REM ディレクトリが存在しない場合は作成

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -J -L -o "%MODEL_DIR%/%%f" "%DOWNLOAD_URL%"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

REM civitaiからControlNetモデルダウンロード
set "MODEL_DIR=%dpath%\ControlNet"
set "DOWNLOAD_URL=https://civitai.com/api/download/models/515749?type=Model&format=SafeTensor"
set "FILES=controlnet852AClone_v10.safetensors"
REM ディレクトリが存在しない場合は作成

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -J -L -o "%MODEL_DIR%/%%f" "%DOWNLOAD_URL%"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)





REM Stable-diffusionモデルダウンロード
set "MODEL_DIR=%dpath%\Stable-diffusion"
set "MODEL_ID=cagliostrolab/animagine-xl-3.1"
set "FILES=animagine-xl-3.1.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    set "FILE_PATH=%MODEL_DIR%\%%f"
    if not exist "!FILE_PATH!" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "!FILE_PATH!"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

endlocal
