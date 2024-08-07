@echo off
setlocal enabledelayedexpansion

REM Set the base path for models
set "dpath=%~dp0models"
echo Base directory set to: %dpath%

goto :main

:download_and_verify
set "FILE_PATH=%~1"
set "DOWNLOAD_URL=%~2"
set "EXPECTED_HASH=%~3"
set "MAX_ATTEMPTS=3"

for /L %%i in (1,1,%MAX_ATTEMPTS%) do (
    echo Attempt %%i of %MAX_ATTEMPTS%
    curl -L "!DOWNLOAD_URL!" -o "!FILE_PATH!"
    
    REM Calculate SHA-256 hash
    for /f "skip=1 tokens=* delims=" %%# in ('certutil -hashfile "!FILE_PATH!" SHA256') do (
        set "ACTUAL_HASH=%%#"
        goto :hash_calculated
    )
    :hash_calculated
    
    if "!ACTUAL_HASH!"=="!EXPECTED_HASH!" (
        echo Hash verification successful.
        exit /b 0
    ) else (
        echo Hash mismatch. Retrying...
        if %%i equ %MAX_ATTEMPTS% (
            echo Warning: Failed to download file with matching hash after %MAX_ATTEMPTS% attempts.
            exit /b 1
        )
    )
)
exit /b

:verify_hash
set "FILE_PATH=%~1"
set "EXPECTED_HASH=%~2"

for /f "skip=1 tokens=* delims=" %%# in ('certutil -hashfile "%FILE_PATH%" SHA256') do (
    set "ACTUAL_HASH=%%#"
    goto :hash_calculated_verify
)
:hash_calculated_verify

if "%ACTUAL_HASH%"=="%EXPECTED_HASH%" (
    echo Hash verification successful for %FILE_PATH%
    exit /b 0
) else (
    echo Hash mismatch for %FILE_PATH%
    echo Expected: %EXPECTED_HASH%
    echo Actual:   %ACTUAL_HASH%
    exit /b 1
)

:download_files_custom
if "%~1"=="" (
    echo No arguments provided to download_files_custom
    exit /b 1
)
echo Downloading files to "%~1" from "%~2" with custom path "%~4"
set "MODEL_DIR=%dpath%\%~1"
set "MODEL_ID=%~2"
set "FILES=%~3"
set "CUSTOM_PATH=%~4"
echo MODEL_DIR: !MODEL_DIR!
echo MODEL_ID: !MODEL_ID!
echo FILES: !FILES!
echo CUSTOM_PATH: !CUSTOM_PATH!

if not exist "!MODEL_DIR!" (
    echo Creating directory !MODEL_DIR!
    mkdir "!MODEL_DIR!"
)

for %%f in (%FILES%) do (
    set "FILE_PATH=!MODEL_DIR!\%%f"
    set "EXPECTED_HASH=!%~1_%%~nf_hash!"
    set "RETRY_COUNT=0"
    :retry_download_custom
    if not exist "!FILE_PATH!" (
        echo Downloading %%f...
        curl -L "https://huggingface.co/!MODEL_ID!/resolve/main/!CUSTOM_PATH!/%%f" -o "!FILE_PATH!"
        if !errorlevel! neq 0 (
            echo Error downloading %%f
        ) else (
            echo Downloaded %%f
            call :verify_hash "!FILE_PATH!" "!EXPECTED_HASH!"
            if !errorlevel! neq 0 (
                echo Hash verification failed for %%f
                set /a RETRY_COUNT+=1
                if !RETRY_COUNT! lss 3 (
                    echo Retry !RETRY_COUNT!/3
                    del "!FILE_PATH!"
                    goto :retry_download_custom
                ) else (
                    echo Hash verification failed after 3 retries. Deleting %%f
                    del "!FILE_PATH!"
                )
            )
        )
    ) else (
        echo %%f already exists. Verifying hash...
        call :verify_hash "!FILE_PATH!" "!EXPECTED_HASH!"
        if !errorlevel! neq 0 (
            echo Hash verification failed for existing file %%f
            del "!FILE_PATH!"
            set "RETRY_COUNT=0"
            goto :retry_download_custom
        )
    )
)
exit /b 0

:download_files_default
if "%~1"=="" (
    echo No arguments provided to download_files_default
    exit /b 1
)
set "MODEL_DIR=%dpath%\%~1"
set "MODEL_ID=%~2"
set "FILES=%~3"

echo MODEL_DIR: !MODEL_DIR!
echo MODEL_ID: !MODEL_ID!
echo FILES: !FILES!

if not exist "!MODEL_DIR!" (
    echo Creating directory !MODEL_DIR!
    mkdir "!MODEL_DIR!"
)

for %%f in (%FILES%) do (
    set "FILE_PATH=!MODEL_DIR!\%%f"
    set "EXPECTED_HASH=!%~1_%%~nf_hash!"
    set "RETRY_COUNT=0"
    :retry_download_default
    if not exist "!FILE_PATH!" (
        echo Downloading %%f...
        curl -L "https://huggingface.co/!MODEL_ID!/resolve/main/%%f" -o "!FILE_PATH!"
        if !errorlevel! neq 0 (
            echo Error downloading %%f
        ) else (
            echo Downloaded %%f
            call :verify_hash "!FILE_PATH!" "!EXPECTED_HASH!"
            if !errorlevel! neq 0 (
                echo Hash verification failed for %%f
                set /a RETRY_COUNT+=1
                if !RETRY_COUNT! lss 3 (
                    echo Retry !RETRY_COUNT!/3
                    del "!FILE_PATH!"
                    goto :retry_download_default
                ) else (
                    echo Hash verification failed after 3 retries. Deleting %%f
                    del "!FILE_PATH!"
                )
            )
        )
    ) else (
        echo %%f already exists. Verifying hash...
        call :verify_hash "!FILE_PATH!" "!EXPECTED_HASH!"
        if !errorlevel! neq 0 (
            echo Hash verification failed for existing file %%f
            del "!FILE_PATH!"
            set "RETRY_COUNT=0"
            goto :retry_download_default
        )
    )
)
exit /b 0

:main
echo Starting main execution

REM Define hashes
set "ControlNet_CN-anytest_v3-50000_am_dim256_hash=9c022669c9225a926c9cbca9baaf40387f2a6d579ea004cd15b2d84b7d130052"
set "ControlNet_CN-anytest_v4-marged_am_dim256_hash=62a63fb885caa1aff54cbceceb0a20968922f45b2d5a370e64b156a982132ffb"
set "ControlNet_control-lora-canny-rank256_hash=21f79f7368eff07f57bcd507ca91c0fc89070d7da182960ff24ed1d58310c3a7"
set "ControlNet_controlnet852AClone_v10_hash=58bae8a373d6a39b33a5d110c5b22894fc86b7b1e189b05b163e69446c7f48ee"
set "ControlNet_Kataragi_lineartXL-lora128_hash=bdc33b12ff20900a7fdea0b239c8ee66180d53b9a13f6f87a9d89d2aee9eac91"
set "ControlNet_CL_am31_pose3D_V7_marged_rank256_hash=a34b7efd90e9820e6c065c66665409f3ce2324eee98237f89a40f41a6218a3ad"
set "Lora_sdxl-testlora-plainmaterial_hash=24df34c2c3abf62c7c1b7ee5432935861b10c1cd38b6997b37743701df6cfe71"
set "Lora_anime01_hash=14fc521897c6298272d1ba62dbe9a41e2c2ea3464b23760c7a956d50dd2b0fd5"
set "Lora_anime02_hash=a6cb70645577e8e5e757dbb511dc913046c492f1b46932d891a684e59108b038"
set "Lora_anime03_hash=5a4c1dedb42b469243c1201213e6e59d9bd0f01edb3a99ce93705200886fb842"
set "Lora_animenuri_hash=afe115b55d2141f3ff39bdad2ea656555568f659b6ab34a8db2dc22ed2410441"
set "Lora_atunuri02_hash=da22a0ed520b03368d2403ed35db6c3c2213c04ab236535133bf7c830fe91b36"
set "Lora_sdxl-testlora-normalmap_04b_dim32_hash=9432dee2c0b9e1636e7c6e9a544571991fc22a455d575ffc1e281a57efee727a"
set "Lora_SDXL_baketu2_hash=d3f935e50967dd7712afdccaa9cdbd115b47c1fb61950553f5b4a70f2d99b3c0"
set "Lora_sdxl_BWLine_hash=07c59708361b3e2e4f0b0c0f232183f5f39c32c31b6b6981b4392ea30d49dd57"
set "Lora_sdxl_BW_bold_Line_hash=eda02fe96a41c60fba6a885072837d24e51a83897eb5ca4ead24a5a248e840b7"
set "Lora_suisai01_hash=f32045c2f8c824f783aebb86206e8dd004038ea9fef7b18b9f5aeff8c0b89d21"
set "Lora_Fixhands_anime_bdsqlsz_V1_hash=7fad91117c8205b11b7e7d37b2820ffc68ff526caabee546d54906907e373ed3"
set "Stable-diffusion_animagine-xl-3.1_hash=e3c47aedb06418c6c331443cd89f2b3b3b34b7ed2102a3d4c4408a8d35aad6b0"
set "tagger_config_hash=ddcdd28facc40ee8d0ef4b16ee3e7c70e4d7b156aff7b0f2ccc180e617eda795"
set "tagger_model_hash=e6774bff34d43bd49f75a47db4ef217dce701c9847b546523eb85ff6dbba1db1"
set "tagger_selected_tags_hash=298633d94d0031d2081c0893f29c82eab7f0df00b08483ba8f29d1e979441217"
set "tagger_sw_jax_cv_config_hash=4dda7ac5591de07f7444ca30f2f89971a21769f1db6279f92ca996d371b761c9"

echo Downloading Tagger model:
call :download_files_default "tagger" "SmilingWolf/wd-swinv2-tagger-v3" "config.json,model.onnx,selected_tags.csv,sw_jax_cv_config.json"

echo Downloading Lora models:
call :download_files_default "Lora" "tori29umai/lineart" "sdxl_BW_bold_Line.safetensors,sdxl_BWLine.safetensors"
call :download_files_default "Lora" "tori29umai/SDXL_shadow" "sdxl-testlora-normalmap_04b_dim32.safetensors,anime01.safetensors,anime02.safetensors,anime03.safetensors"
call :download_files_default "Lora" "tori29umai/flat_color" "suisai01.safetensors,atunuri02.safetensors,animenuri.safetensors,SDXL_baketu2.safetensors"
call :download_files_default "Lora" "bdsqlsz/stable-diffusion-xl-anime-V5" "Fixhands_anime_bdsqlsz_V1.safetensors"
call :download_files_custom "Lora" "2vXpSwA7/iroiro-lora" "sdxl-testlora-plainmaterial.safetensors" "test3" 

echo Downloading ControlNet models:
call :download_files_custom "ControlNet" "2vXpSwA7/iroiro-lora" "CN-anytest_v3-50000_am_dim256.safetensors,CN-anytest_v4-marged_am_dim256.safetensors" "test_controlnet2" 
call :download_files_custom "ControlNet" "stabilityai/control-lora" "control-lora-canny-rank256.safetensors" "control-LoRAs-rank256"
call :download_files_default "ControlNet" "kataragi/ControlNet-LineartXL" "Kataragi_lineartXL-lora128.safetensors"
call :download_files_default "ControlNet" "tori29umai/CN_pose3D_V7" "CL_am31_pose3D_V7_marged_rank256.safetensors"

echo Downloading Stable-diffusion model:
call :download_files_default "Stable-diffusion" "cagliostrolab/animagine-xl-3.1" "animagine-xl-3.1.safetensors"

echo Downloading from Civitai:
set "MODEL_DIR=!dpath!\ControlNet"
set "DOWNLOAD_URL=https://civitai.com/api/download/models/515749?type=Model&format=SafeTensor"
set "FILES=controlnet852AClone_v10.safetensors"

if not exist "!MODEL_DIR!" (
    echo Creating directory !MODEL_DIR!
    mkdir "!MODEL_DIR!"
)

for %%f in (%FILES%) do (
    set "FILE_PATH=!MODEL_DIR!\%%f"
    set "EXPECTED_HASH=!ControlNet_controlnet852AClone_v10_hash!"
    set "RETRY_COUNT=0"
    :retry_download_civitai
    if not exist "!FILE_PATH!" (
        echo Downloading %%f from Civitai...
        curl -J -L -o "!FILE_PATH!" "%DOWNLOAD_URL%"
        if !errorlevel! neq 0 (
            echo Error downloading %%f from Civitai
        ) else (
            echo Downloaded %%f
            call :verify_hash "!FILE_PATH!" "!EXPECTED_HASH!"
            if !errorlevel! neq 0 (
                echo Hash verification failed for %%f
                echo Expected: !EXPECTED_HASH!
                echo Actual:   !ACTUAL_HASH!
                set /a RETRY_COUNT+=1
                if !RETRY_COUNT! lss 3 (
                    echo Retry !RETRY_COUNT!/3
                    del "!FILE_PATH!"
                    goto :retry_download_civitai
                ) else (
                    echo Hash verification failed after 3 retries. Deleting %%f
                    del "!FILE_PATH!"
                )
            )
        )
    ) else (
        echo %%f already exists. Verifying hash...
        call :verify_hash "!FILE_PATH!" "!EXPECTED_HASH!"
        if !errorlevel! neq 0 (
            echo Hash verification failed for existing file %%f
            echo Expected: !EXPECTED_HASH!
            echo Actual:   !ACTUAL_HASH!
            del "!FILE_PATH!"
            set "RETRY_COUNT=0"
            goto :retry_download_civitai
        )
    )
)

echo Script execution completed
echo Press Enter to close the script...
pause > nul
exit /b
endlocal