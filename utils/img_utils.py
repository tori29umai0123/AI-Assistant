from PIL import Image, ImageOps
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

def invert_process(image_path):
    # 画像を開き、RGBA形式に変換して透過情報を保持
    img = Image.open(image_path)
    img = img.convert("RGBA")

    canvas_image = Image.new('RGBA', img.size, (255, 255, 255, 255))
    
    # 画像をキャンバスにペーストし、透過部分が白色になるように設定
    canvas_image.paste(img, (0, 0), img)

    # RGBAからRGBに変換し、透過部分を白色にする
    image_pil = canvas_image.convert("RGB")

    # image_pilを白黒反転する
    invert = ImageOps.invert(image_pil)
    
    return invert


def flatline_process(image_path):
    def DoG_filter(image, kernel_size=0, sigma=1.0, k_sigma=2.0, gamma=1.5):
        g1 = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
        g2 = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma * k_sigma)
        return g1 - gamma * g2

    def XDoG_filter(image, kernel_size=0, sigma=1.4, k_sigma=1.6, epsilon=0, phi=10, gamma=0.98):
        epsilon /= 255
        dog = DoG_filter(image, kernel_size, sigma, k_sigma, gamma)
        dog /= dog.max()
        e = 1 + np.tanh(phi * (dog - epsilon))
        e[e >= 1] = 1
        return (e * 255).astype('uint8')

    def binarize_image(image):
        _, binarized = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binarized

    def skeletonize_and_dilate_image(image):
        inverted = cv2.bitwise_not(image)
        skeleton = cv2.ximgproc.thinning(inverted, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
        return cv2.bitwise_not(skeleton)

    def process_XDoG(image, kernel_size=0, sigma=1.4, k_sigma=1.6, epsilon=0, phi=10, gamma=0.98):
        xdog_image = XDoG_filter(image, kernel_size, sigma, k_sigma, epsilon, phi, gamma)
        binarized_image = binarize_image(xdog_image)
        final_image = skeletonize_and_dilate_image(binarized_image)
        final_image = 255 - final_image
        final_image_pil = Image.fromarray(final_image)
        return final_image_pil

    # 画像を開き、RGBA形式に変換して透過情報を保持
    img = Image.open(image_path)
    img = img.convert("RGBA")

    canvas_image = Image.new('RGBA', img.size, (255, 255, 255, 255))
    
    # 画像をキャンバスにペーストし、透過部分が白色になるように設定
    canvas_image.paste(img, (0, 0), img)

    # RGBAからRGBに変換し、透過部分を白色にする
    image_pil = canvas_image.convert("RGB")
    
    # OpenCVが扱える形式に変換
    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    image_gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    flatLine = process_XDoG(image_gray, kernel_size=0, sigma=1.4, k_sigma=1.6, epsilon=0, phi=10, gamma=0.98)
    return flatLine



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

def resize_image_aspect_ratio(image):
    # 元の画像サイズを取得
    original_width, original_height = image.size

    # アスペクト比を計算
    aspect_ratio = original_width / original_height

    # 標準のアスペクト比サイズを定義
    sizes = {
        1: (1024, 1024),  # 正方形
        4/3: (1152, 896),  # 横長画像
        3/2: (1216, 832),
        16/9: (1344, 768),
        21/9: (1568, 672),
        3/1: (1728, 576),
        1/4: (512, 2048),  # 縦長画像
        1/3: (576, 1728),
        9/16: (768, 1344),
        2/3: (832, 1216),
        3/4: (896, 1152)
    }

    # 最も近いアスペクト比を見つける
    closest_aspect_ratio = min(sizes.keys(), key=lambda x: abs(x - aspect_ratio))
    target_width, target_height = sizes[closest_aspect_ratio]

    # リサイズ処理
    resized_image = image.resize((target_width, target_height), Image.ANTIALIAS)

    return resized_image

def base_generation(size, color):
    canvas = Image.new("RGBA", size, color)  # 白背景のキャンバスを作成 
    return canvas


def make_base_pil(image_path):
    # 処理対象の基本画像を生成する
    # 画像を開き、白色背景に変換した上でアスペクト比に基づくリサイズを行う
    base_pil = Image.open(image_path).convert("RGBA")
    base_pil = resize_image_aspect_ratio(base_pil)
    white_bg = Image.new("RGBA", base_pil.size, "WHITE")
    white_bg.paste(base_pil, mask=base_pil)
    base_pil = resize_image_aspect_ratio(white_bg).convert("RGB")
    return base_pil