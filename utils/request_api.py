import requests
import json
import base64
from datetime import datetime
import os
import itertools
import random
import re
from PIL import Image, PngImagePlugin, ImageEnhance, ImageFilter, ImageOps
import io
import glob
import cv2


def build_payload(prompt, nega, w, h, unit1, unit2, encoded_base, encoded_mask, image_fidelity, lineart_fidelity, mode):
    if mode == "i2i":
        return {
            "init_images": [encoded_base],
            "mask": encoded_mask,
            "mask_blur": 4,
            "inpainting_fill": 1,
            "denoising_strength": image_fidelity,
            "prompt": prompt,
            "negative_prompt": nega,
            "seed": -1,
            "sampler_name": "Euler a",
            "steps": 20,
            "cfg_scale": 7,
            "width": w,
            "height": h,
        } 
    
    elif mode == "lineart" or mode == "normalmap":
        return {
            "init_images": [encoded_base],
            "denoising_strength": image_fidelity,
            "prompt": prompt,
            "negative_prompt": nega,
            "seed": -1,
            "sampler_name": "Euler a",
            "steps": 20,
            "cfg_scale": 7,
            "width": w,
            "height": h,
            "alwayson_scripts": {"ControlNet": {"args": [unit1]}},
        }
    
    elif mode == "anime_shadow":
        return {
            "init_images": [encoded_mask],
            "denoising_strength": image_fidelity,
            "prompt": prompt,
            "negative_prompt": nega,
            "seed": -1,
            "sampler_name": "Euler a",
            "steps": 20,
            "cfg_scale": 7,
            "width": w,
            "height": h,
            "alwayson_scripts": {"ControlNet": {"args": [unit1, unit2]}},
        }        

def send_post_request(url, payload):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response


def save_image(data, url, file_name, image_size):
    image_string = data["images"][0]
    image_bytes = base64.b64decode(image_string)

    png_payload = {
        "image": "data:image/png;base64," + image_string
    }
    response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
    image_info = response2.json().get("info")

    image = Image.open(io.BytesIO(image_bytes))
    pnginfo = PngImagePlugin.PngInfo()
    if image_info:  # Ensure image_info is not None
        pnginfo.add_text("parameters", image_info)
    image = image.resize(image_size, Image.LANCZOS)
    image.save(file_name, pnginfo=pnginfo)
    return image


def create_and_save_images(input_url, prompt, nega, base_pil, canny_pil, mask_pil, image_size, output_path, mode, image_fidelity, lineart_fidelity):
    url = f"{input_url}/sdapi/v1/img2img"
    w, h =  base_pil.size
    if mode == "i2i":
        base_bytes = io.BytesIO()
        base_pil.save(base_bytes, format='PNG')
        encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
        mask_bytes = io.BytesIO()
        mask_pil.save(mask_bytes, format='PNG')
        encoded_mask = base64.b64encode(mask_bytes.getvalue()).decode('utf-8')
        encoded_canny = None
        unit1 = None
        unit2 = None
        
    #modeがlineartかnormalmapの場合
    elif mode == "lineart" or mode == "normalmap":
        base_bytes = io.BytesIO()
        base_pil.save(base_bytes, format='PNG')
        encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
        mask_bytes = io.BytesIO()
        mask_pil.save(mask_bytes, format='PNG')
        encoded_mask = base64.b64encode(mask_bytes.getvalue()).decode('utf-8')
        canny_bytes = io.BytesIO()
        canny_pil.save(canny_bytes, format='PNG')
        encoded_canny = base64.b64encode(canny_bytes.getvalue()).decode('utf-8')

        unit1 = {
            "image": encoded_canny,
            "mask_image": encoded_mask,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 1280,
            "resize_mode": "Just Resize",
            "threshold_a": 64,
            "threshold_b": 64,
            "weight": lineart_fidelity,
            "module": "canny",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None

    elif mode == "lineart":
        base_bytes = io.BytesIO()
        base_pil.save(base_bytes, format='PNG')
        encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
        mask_bytes = io.BytesIO()
        mask_pil.save(mask_bytes, format='PNG')
        encoded_mask = base64.b64encode(mask_bytes.getvalue()).decode('utf-8')
        canny_bytes = io.BytesIO()
        canny_pil.save(canny_bytes, format='PNG')
        encoded_canny = base64.b64encode(canny_bytes.getvalue()).decode('utf-8')

        unit1 = {
            "image": encoded_canny,
            "mask_image": encoded_mask,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 1280,
            "resize_mode": "Just Resize",
            "threshold_a": 64,
            "threshold_b": 64,
            "weight": lineart_fidelity,
            "module": "canny",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None


    elif mode == "normalmap":
        base_bytes = io.BytesIO()
        base_pil.save(base_bytes, format='PNG')
        encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
        mask_bytes = io.BytesIO()
        mask_pil.save(mask_bytes, format='PNG')
        encoded_mask = base64.b64encode(mask_bytes.getvalue()).decode('utf-8')
        canny_bytes = io.BytesIO()
        canny_pil.save(canny_bytes, format='PNG')
        encoded_canny = base64.b64encode(canny_bytes.getvalue()).decode('utf-8')

        unit1 = {
            "image": encoded_canny,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1.0,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 1280,
            "resize_mode": "Just Resize",
            "threshold_a": 64,
            "threshold_b": 64,
            "weight": lineart_fidelity,
            "module": "canny",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None




    elif mode == "anime_shadow":
        base_bytes = io.BytesIO()
        base_pil.save(base_bytes, format='PNG')
        encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
        mask_bytes = io.BytesIO()
        mask_pil.save(mask_bytes, format='PNG')
        encoded_mask = base64.b64encode(mask_bytes.getvalue()).decode('utf-8')
        canny_bytes = io.BytesIO()
        canny_pil.save(canny_bytes, format='PNG')
        encoded_canny = base64.b64encode(canny_bytes.getvalue()).decode('utf-8')

        unit1 = {
            "image": encoded_canny,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1.0,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 1280,
            "resize_mode": "Just Resize",
            "threshold_a": 64,
            "threshold_b": 64,
            "weight": lineart_fidelity,
            "module": "canny",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = {
            "image": encoded_mask,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1.0,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 1280,
            "resize_mode": "Just Resize",
            "threshold_a": 64,
            "threshold_b": 64,
            "weight": 1,
            "module": "None",
            "model": "cnlllite-anystyle_v3-step00004000 [79bd7642]",
            "save_detected_map": None,
            "hr_option": "Both"
        }         

    payload = build_payload(prompt, nega, w, h, unit1, unit2, encoded_base, encoded_mask, image_fidelity, lineart_fidelity, mode)
    response = send_post_request(url, payload)
    image_data = response.json()

    if "images" in image_data and image_data["images"]:
        output_pil = save_image(image_data, input_url, output_path, image_size)
        print(f"Downloaded {output_path} to local")
        return output_pil
    else:
        print("Failed to generate image. 'images' key not found in the response.")

def get_model(url):
    sd_models = requests.get(f"{url}/sdapi/v1/sd-models").json()
    sd_model_names = [i["title"] for i in sd_models]
    current_model_name = requests.get(f"{url}/sdapi/v1/options").json()["sd_model_checkpoint"]
    return sd_model_names, current_model_name

def get_controlnet_model(url):
    cn_models = requests.get(f"{url}/controlnet/model_list").json()
    return cn_models

def set_model(url, sd_model_name):
    option_payload = {
        "sd_model_checkpoint":sd_model_name,
    }
    response = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)