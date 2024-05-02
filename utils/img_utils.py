from PIL import Image
import numpy as np
import cv2


def canny_process(image_path, threshold1, threshold2):
    # 画像を開き、RGBA形式に変換して透過情報を保持
    img = Image.open(image_path)
    img = img.convert("RGBA")

    canvas_image = Image.new('RGBA', img.size, (255, 255, 255, 255))
    
    # 画像をキャンバスにペーストし、透過部分が白色になるように設定
    canvas_image.paste(img, (0, 0), img)

    # RGBAからRGBに変換し、透過部分を白色にする
    image_pil = canvas_image.convert("RGB")
    image_np = np.array(image_pil)
    
    # グレースケール変換
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    # Cannyエッジ検出
    edges = cv2.Canny(gray, threshold1, threshold2)
    
    canny = Image.fromarray(edges)
    
    
    return canny

def mask_process(image_path):
    # 画像をRGBAで読み込み、アルファチャンネルを考慮
    img = Image.open(image_path).convert("RGBA")
    img_rgba = img.convert("RGBA")
    canvas = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))  # 白背景のキャンバスを作成
    img_with_background = Image.alpha_composite(canvas, img_rgba)
    
    # OpenCVが扱える形式に変換
    img_with_background = cv2.cvtColor(np.array(img_with_background), cv2.COLOR_RGBA2BGR)
    img = cv2.bitwise_not(img_with_background)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ret, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=lambda x: cv2.contourArea(x))
    mask = np.zeros_like(img_with_background)
    cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)
    mask = Image.fromarray(mask)
    return mask

def multiply_images(line_pil, shadow_pil):
    # 画像のモードを確認し、必要に応じてRGBAに変換
    if line_pil.mode != 'RGBA':
        line_pil = line_pil.convert('RGBA')
    if shadow_pil.mode != 'RGBA':
        shadow_pil = shadow_pil.convert('RGBA')
    
    # 画像のサイズを確認し、異なる場合はエラーを投げる
    if line_pil.size != shadow_pil.size:
        raise ValueError("Images must have the same dimensions")
    
    # 乗算処理を行う
    result_image = Image.new('RGBA', line_pil.size)
    for x in range(line_pil.width):
        for y in range(line_pil.height):
            pixel_line = line_pil.getpixel((x, y))
            pixel_shadow = shadow_pil.getpixel((x, y))
            # 各チャンネルごとに乗算し、255で割って正規化
            r = (pixel_line[0] * pixel_shadow[0]) // 255
            g = (pixel_line[1] * pixel_shadow[1]) // 255
            b = (pixel_line[2] * pixel_shadow[2]) // 255
            a = (pixel_line[3] * pixel_shadow[3]) // 255
            result_image.putpixel((x, y), (r, g, b, a))
    
    return result_image

def resize_image_aspect_ratio(image, max_length=1280):
    # 元の画像サイズを取得
    original_width, original_height = image.size

    # アスペクト比を計算
    aspect_ratio = original_width / original_height

    # 長辺がmax_lengthになるように新しいサイズを計算
    if original_width > original_height:
        new_width = max_length
        new_height = round(max_length / aspect_ratio)
    else:
        new_height = max_length
        new_width = round(max_length * aspect_ratio)

    # 新しい幅と高さを32の倍数に調整
    new_width = (new_width // 32) * 32
    new_height = (new_height // 32) * 32

    # 新しいサイズで画像をリサイズ
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_image

def base_generation(size, color):
    canvas = Image.new("RGBA", size, color)  # 白背景のキャンバスを作成 
    return canvas
