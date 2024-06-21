@echo off
setlocal

:: モデルディレクトリの基本パスを実行ディレクトリのmodelsサブディレクトリに設定
set "dpath=%~dp0models"

:: Taggerモデルダウンロード
set "MODEL_DIR=%dpath%\tagger"
set "MODEL_ID=SmilingWolf/wd-swinv2-tagger-v3"
set "FILES=config.json model.onnx selected_tags.csv sw_jax_cv_config.json"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    if not exist "%MODEL_DIR%\%%f" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "%MODEL_DIR%\%%f"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)

:: Loraモデルダウンロード (複数)
set LORA_MODELS="2vXpSwA7/iroiro-lora sdxl-testlora-normalmap_04b_dim32.safetensors test3" ^
                "tori29umai/lineart sdxl_BW_bold_Line.safetensors" ^
                "tori29umai/lineart sdxl_BWLine.safetensors" ^
                "tori29umai/SDXL_shadow anime01.safetensors" ^
                "tori29umai/SDXL_shadow anime02.safetensors" ^
                "tori29umai/SDXL_shadow anime03.safetensors" ^
                "tori29umai/flat_color SDXL_baketu2.safetensors"

for %%i in (%LORA_MODELS%) do (
    for /f "tokens=1,2,3" %%a in ("%%i") do (
        set "MODEL_ID=%%a"
        set "FILES=%%b"
        set "SUBDIR=%%c"
        set "MODEL_DIR=%dpath%\Lora"
        if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
        if not exist "%MODEL_DIR%\%%b" (
            if not "%%c"=="" (
                curl -L "https://huggingface.co/%%a/resolve/main/%%c/%%b" -o "%MODEL_DIR%\%%b"
            ) else (
                curl -L "https://huggingface.co/%%a/resolve/main/%%b" -o "%MODEL_DIR%\%%b"
            )
            echo Downloaded %%b
        ) else (
            echo %%b already exists.
        )
    )
)

:: ControlNetモデルダウンロード (複数)
set CONTROLNET_MODELS="2vXpSwA7/iroiro-lora CN-anytest_v3-50000_am_dim256.safetensors test_controlnet2" ^
                      "2vXpSwA7/iroiro-lora CN-anytest_v4-marged_am_dim256.safetensors test_controlnet2" ^
                      "stabilityai/control-lora control-lora-canny-rank256.safetensors control-LoRAs-rank256" ^
                      "kataragi/ControlNet-LineartXL Kataragi_lineartXL-lora128.safetensors"

for %%i in (%CONTROLNET_MODELS%) do (
    for /f "tokens=1,2,3" %%a in ("%%i") do (
        set "MODEL_ID=%%a"
        set "FILES=%%b"
        set "SUBDIR=%%c"
        set "MODEL_DIR=%dpath%\ControlNet"
        if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
        if not exist "%MODEL_DIR%\%%b" (
            if not "%%c"=="" (
                curl -L "https://huggingface.co/%%a/resolve/main/%%c/%%b" -o "%MODEL_DIR%\%%b"
            ) else (
                curl -L "https://huggingface.co/%%a/resolve/main/%%b" -o "%MODEL_DIR%\%%b"
            )
            echo Downloaded %%b
        ) else (
            echo %%b already exists.
        )
    )
)

:: civitaiからControlNetモデルダウンロード
set CIVITAI_MODELS="https://civitai.com/api/download/models/506961?type=Model&format=SafeTensor controlnet852A_veryhard.safetensors" ^
                   "https://civitai.com/api/download/models/515749?type=Model&format=SafeTensor controlnet852AClone_v10.safetensors"

for %%i in (%CIVITAI_MODELS%) do (
    for /f "tokens=1,2" %%a in ("%%i") do (
        set "DOWNLOAD_URL=%%a"
        set "FILES=%%b"
        set "MODEL_DIR=%dpath%\ControlNet"
        if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
        if not exist "%MODEL_DIR%\%%b" (
            curl -J -L -o "%MODEL_DIR%\%%b" "%%a"
            echo Downloaded %%b
        ) else (
            echo %%b already exists.
        )
    )
)

:: Stable-diffusionモデルダウンロード
set "MODEL_DIR=%dpath%\Stable-diffusion"
set "MODEL_ID=cagliostrolab/animagine-xl-3.1"
set "FILES=animagine-xl-3.1.safetensors"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
for %%f in (%FILES%) do (
    if not exist "%MODEL_DIR%\%%f" (
        curl -L "https://huggingface.co/%MODEL_ID%/resolve/main/%%f" -o "%MODEL_DIR%\%%f"
        echo Downloaded %%f
    ) else (
        echo %%f already exists.
    )
)
