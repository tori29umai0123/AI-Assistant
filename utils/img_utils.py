import numpy as np
from PIL import Image, ImageOps, ImageFilter
import cv2
from collections import defaultdict
from skimage.color import rgb2lab, deltaE_ciede2000


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
    canvas = Image.new("RGBA", size, color) 
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

def noline_process(input_image_path):
    def get_major_colors(image, threshold_percentage):
        if image.mode != 'RGB':
            image = image.convert('RGB')
        color_count = defaultdict(int)
        for pixel in image.getdata():
            color_count[pixel] += 1
        total_pixels = image.width * image.height
        return [(color, count) for color, count in color_count.items() if (count / total_pixels) >= threshold_percentage]

    def consolidate_colors(major_colors, threshold):
        colors_lab = [rgb2lab(np.array([[color]], dtype=np.float32)/255.0).reshape(3) for color, _ in major_colors]
        i = 0
        while i < len(colors_lab):
            j = i + 1
            while j < len(colors_lab):
                if deltaE_ciede2000(colors_lab[i], colors_lab[j]) < threshold:
                    if major_colors[i][1] >= major_colors[j][1]:
                        major_colors[i] = (major_colors[i][0], major_colors[i][1] + major_colors[j][1])
                        major_colors.pop(j)
                        colors_lab.pop(j)
                    else:
                        major_colors[j] = (major_colors[j][0], major_colors[j][1] + major_colors[i][1])
                        major_colors.pop(i)
                        colors_lab.pop(i)
                    continue
                j += 1
            i += 1
        return major_colors

    def generate_distant_colors(consolidated_colors, distance_threshold):
        consolidated_lab = [rgb2lab(np.array([color], dtype=np.float32) / 255.0).reshape(3) for color, _ in consolidated_colors]
        max_attempts = 10000
        for _ in range(max_attempts):
            random_rgb = np.random.randint(0, 256, size=3)
            random_lab = rgb2lab(np.array([random_rgb], dtype=np.float32) / 255.0).reshape(3)
            if all(deltaE_ciede2000(base_color_lab, random_lab) > distance_threshold for base_color_lab in consolidated_lab):
                return tuple(random_rgb)
        return (128, 128, 128)

    def line_color(image, mask, new_color):
        data = np.array(image)
        data[mask, :3] = new_color
        return Image.fromarray(data)

    def replace_color(image, color_1, blur_radius=2):
        data = np.array(image)
        original_shape = data.shape
        channels = original_shape[2] if len(original_shape) > 2 else 1
        data = data.reshape(-1, channels)
        color_1 = np.array(color_1)
        matches = np.all(data[:, :3] == color_1, axis=1)
        mask = np.zeros(data.shape[0], dtype=bool)

        while np.any(matches):
            new_matches = np.zeros_like(matches)
            for i in range(len(data)):
                if matches[i]:
                    x, y = divmod(i, original_shape[1])
                    neighbors = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
                    valid_neighbors = [data[nx * original_shape[1] + ny, :3] for nx, ny in neighbors if 0 <= nx < original_shape[0] and 0 <= ny < original_shape[1] and not matches[nx * original_shape[1] + ny]]
                    if valid_neighbors:
                        new_color = np.mean(valid_neighbors, axis=0).astype(np.uint8)
                        data[i, :3] = new_color
                        mask[i] = True
                    else:
                        new_matches[i] = True
            matches = new_matches
            if not np.any(matches):
                break

        data = data.reshape(original_shape)
        mask = mask.reshape(original_shape[:2])
        result_image = Image.fromarray(data, 'RGBA')
        blurred_image = result_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        blurred_data = np.array(blurred_image)
        np.copyto(data, blurred_data, where=mask[..., None])
        return Image.fromarray(data, 'RGBA')

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


    def process_XDoG(image_path):
        kernel_size=0
        sigma=1.4
        k_sigma=1.6
        epsilon=0
        phi=10
        gamma=0.98

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        xdog_image = XDoG_filter(image, kernel_size, sigma, k_sigma, epsilon, phi, gamma)
        binarized_image = binarize_image(xdog_image)
        final_image = Image.fromarray(binarized_image)
        return final_image

    rgb_image = Image.open(input_image_path).convert("RGBA")
    lineart = process_XDoG(input_image_path).convert('L')
    lineart = lineart.point(lambda x: 0 if x < 200 else 255)
    lineart = ImageOps.invert(lineart)
    kernel = np.ones((3, 3), np.uint8)
    lineart = cv2.dilate(np.array(lineart), kernel, iterations=1)
    lineart = Image.fromarray(lineart)
    mask = np.array(lineart) == 255
    major_colors = get_major_colors(rgb_image, threshold_percentage=0.05)
    major_colors = consolidate_colors(major_colors, 10)
    new_color_1 = generate_distant_colors(major_colors, 100)
    filled_image = line_color(rgb_image, mask, new_color_1)
    replace_color_image = replace_color(filled_image, new_color_1, 2).convert('RGB')
    return replace_color_image
