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

def build_payload(prompt, nega, w, h, cn_args, encoded_base, encoded_mask, image_fidelity,  mode, override_settings):
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
            "override_settings": override_settings,
            "override_settings_restore_afterwards": False
        } 
    
    elif mode == "lineart" or "lineart2" or mode == "normalmap":
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
            "alwayson_scripts": {"ControlNet": {"args": cn_args}},
            "override_settings": override_settings,
            "override_settings_restore_afterwards": False
        }
    
    elif mode == "anime_shadow":
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
            "alwayson_scripts": {"ControlNet": {"args": cn_args}},
            "override_settings": override_settings,
            "override_settings_restore_afterwards": False
        }        

    elif mode == "resize":
        return {
            "init_images": [encoded_base],
            "denoising_strength": image_fidelity,
            "prompt": prompt,
            "negative_prompt": nega,
            "seed": -1,
            "sampler_name": "Euler a",
            "steps": 30,
            "cfg_scale": 7,
            "width": w,
            "height": h,
            "alwayson_scripts": {"ControlNet": {"args": cn_args}},
            "override_settings": override_settings,
            "override_settings_restore_afterwards": False
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
    response = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
    image_info = response.json().get("info")

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
    override_settings = {}
    override_settings["CLIP_stop_at_last_layers"] = 2 
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
        cn_args = None
        
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
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": lineart_fidelity,
            "module":"None",
            "model": "control-lora-canny-rank256 [ec2dbbe4]",
            "save_detected_map": None,
            "hr_option": "Both"
        }

        unit2 = None
        cn_args = [unit1]

    elif mode == "lineart2":
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
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": lineart_fidelity,
            "module": "None",
            "model": "controlnet852A_veryhard [8a1dc920]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None
        cn_args = [unit1]


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
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": lineart_fidelity,
            "module": "None",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None
        cn_args = [unit1]



    elif mode == "anime_shadow":
        base_bytes = io.BytesIO()
        base_pil.save(base_bytes, format='PNG')
        encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
        canny_bytes = io.BytesIO()
        canny_pil.save(canny_bytes, format='PNG')
        encoded_canny = base64.b64encode(canny_bytes.getvalue()).decode('utf-8')
        mask_bytes = io.BytesIO()
        mask_pil.save(mask_bytes, format='PNG')
        encoded_mask = base64.b64encode(mask_bytes.getvalue()).decode('utf-8')
 
        unit1 = {
            "image": encoded_mask,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 0.35,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": 0.65,
            "module": "blur_gaussian",
            "threshold_a": 10.0,
            "model": "controlnet852AClone_v10 [808807b2]",
            "save_detected_map": None,
            "hr_option": "Both"
        }         
        unit2 = {
            "image": encoded_canny,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": 1.25,
            "module": "None",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        cn_args = [unit1, unit2]
    payload = build_payload(prompt, nega, w, h, cn_args, encoded_base, encoded_mask, image_fidelity, mode, override_settings)
    response = send_post_request(url, payload)
    image_data = response.json()

    if "images" in image_data and image_data["images"]:
        output_pil = save_image(image_data, input_url, output_path, image_size)
        print(f"Downloaded {output_path} to local")
        return output_pil
    else:
        print("Failed to generate image. 'images' key not found in the response.")

def upscale_and_save_images(input_url, prompt, nega, base_pil, output_path, image_size):

    w =  image_size[0]
    h =  image_size[1]
    base_bytes = io.BytesIO()
    base_pil.save(base_bytes, format='PNG')
    encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
    
    url = f"{input_url}/sdapi/v1/extra-single-image"

    payload = {
        "resize_mode": 0,
        "show_extras_results": False,
        "gfpgan_visibility": 0,
        "codeformer_visibility": 0,
        "codeformer_weight": 0,
        "upscaling_resize": 4,
        "upscaling_resize_w": 512,
        "upscaling_resize_h": 512,
        "upscaling_crop": False,
        "upscaler_1": "R-ESRGAN 4x+ Anime6B",
        "upscaler_2": "R-ESRGAN 4x+ Anime6B",
        "extras_upscaler_2_visibility": 0.25,
        "upscale_first": False,
        "image": encoded_base
    }
    response = send_post_request(url, payload)
    image_data = response.json()
    if "image" in image_data:
        image_string = image_data["image"]
        image_bytes = base64.b64decode(image_string)
        resized_image = Image.open(io.BytesIO(image_bytes))
        url = f"{input_url}/sdapi/v1/img2img"
        resized_bytes = io.BytesIO()
        resized_image.save(resized_bytes, format='PNG')
        encoded_resize = base64.b64encode(resized_bytes.getvalue()).decode('utf-8')

        unit1 = {
            "image": encoded_base,
            "mask_image": None,
            "control_mode": "ControlNet is more important",
            "enabled": True,
            "guidance_end": 1.0,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": 0.8,
            "module": "None",
            "model": "controlnet852AClone_v10 [808807b2]",
            "save_detected_map": None,
            "hr_option": "Both"
        }

        unit2 = {
            "image": encoded_base,
            "mask_image": None,
            "control_mode": "ControlNet is more important",
            "enabled": True,
            "guidance_end": 1.0,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": 0.8,
            "module": "lineart_realistic",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        override_settings = {}
        override_settings["CLIP_stop_at_last_layers"] = 2
        cn_args = [unit1, unit2]
        encoded_mask = None
        image_fidelity = 0.45
        mode = "resize"
        payload = payload = build_payload(prompt, nega, w, h, cn_args, encoded_resize, encoded_mask, image_fidelity, mode, override_settings)
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