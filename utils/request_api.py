import base64
import io
import json

import requests
from PIL import Image, PngImagePlugin


def build_payload(prompt, nega, w, h, cn_args, encoded_base, encoded_mask, image_fidelity, mode, override_settings):
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


def prepare_image(pil_image):
    bytes_io = io.BytesIO()
    pil_image.save(bytes_io, format='PNG')
    encoded_image = base64.b64encode(bytes_io.getvalue()).decode('utf-8')
    return encoded_image


def create_and_save_images(input_url, prompt, nega, base_pil, mask_pil, image_size, output_path, mode, image_fidelity,
                           cn_args):
    url = f"{input_url}/sdapi/v1/img2img"
    w, h = base_pil.size
    override_settings = {}
    override_settings["CLIP_stop_at_last_layers"] = 2

    encoded_base = prepare_image(base_pil)
    encoded_mask = prepare_image(mask_pil) if mask_pil else None
    if cn_args:
        for i, cn_arg in enumerate(cn_args):
            if cn_arg["image"]:
                if cn_arg["image"] is encoded_mask:
                    cn_args[i]["image"] = encoded_mask
                elif cn_arg["image"] is encoded_base:
                    cn_args[i]["image"] = encoded_base
                else:
                    cn_args[i]["image"] = prepare_image(cn_arg["image"])
            if cn_arg["mask_image"]:
                if cn_arg["mask_image"] is encoded_mask:
                    cn_args[i]["mask_image"] = encoded_mask
                elif cn_arg["mask_image"] is encoded_base:
                    cn_args[i]["mask_image"] = encoded_base
                else:
                    cn_args[i]["mask_image"] = prepare_image(cn_arg["mask_image"])

    payload = build_payload(prompt, nega, w, h, cn_args, encoded_base, encoded_mask, image_fidelity, mode,
                            override_settings)
    response = send_post_request(url, payload)
    image_data = response.json()

    if "images" in image_data and image_data["images"]:
        output_pil = save_image(image_data, input_url, output_path, image_size)
        print(f"Downloaded {output_path} to local")
        return output_pil
    else:
        print("Failed to generate image. 'images' key not found in the response.")


def upscale_and_save_images(input_url, prompt, nega, base_pil, output_path, image_size):
    w = image_size[0]
    h = image_size[1]
    base_bytes = io.BytesIO()
    base_pil.save(base_bytes, format='PNG')
    encoded_base = base64.b64encode(base_bytes.getvalue()).decode('utf-8')
    url = f"{input_url}/sdapi/v1/img2img"
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
    payload = payload = build_payload(prompt, nega, w, h, cn_args, encoded_base, encoded_mask, image_fidelity, mode,
                                      override_settings)
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
        "sd_model_checkpoint": sd_model_name,
    }
    response = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)
