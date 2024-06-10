import gradio as gr
import numpy as np
import torch
from PIL import Image
from torchvision.transforms.functional import to_pil_image, to_tensor

from AI_Assistant_modules.output_image_gui import OutputImage

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class Lighting:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def layout(self, transfer_target_lang_key=None):
        lang_util = self.app_config.lang_util
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        self.input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor",
                                                    source="upload",
                                                    type='filepath', interactive=True)
                    with gr.Column():
                        pass
                with gr.Row():
                    lighting_option = gr.Dropdown(
                        show_label=False,
                        type='index',
                        choices=[
                            lang_util.get_text("light_source_directly_above"),
                            lang_util.get_text("light_source_upper_left_diagonal"),
                            lang_util.get_text("light_source_upper_right_diagonal"),
                            lang_util.get_text("light_source_directly_left"),
                            lang_util.get_text("light_source_directly_right"),
                            lang_util.get_text("light_source_directly_below"),
                        ],
                    )
                with gr.Row():
                    light_yaw = gr.Slider(label=lang_util.get_text("light_yaw"), minimum=-180, maximum=180, value=60,
                                          step=0.1)
                    light_pitch = gr.Slider(label=lang_util.get_text("light_pitch"), minimum=-90, maximum=90, value=-60,
                                            step=0.1)
                    specular_power = gr.Slider(label=lang_util.get_text("specular_power"), minimum=10, maximum=100,
                                               value=30, step=0.01)
                    normal_diffuse_strength = gr.Slider(label=lang_util.get_text("normal_diffuse_strength"), minimum=0,
                                                        maximum=5.0, value=1.00, step=0.01)
                    specular_highlights_strength = gr.Slider(label=lang_util.get_text("specular_highlights_strength"),
                                                             minimum=0, maximum=5.0, value=0.80, step=0.01)
                    total_gain = gr.Slider(label=lang_util.get_text("total_gain"), minimum=-0, maximum=1.0, value=0.60,
                                           step=0.01)
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)

        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image], outputs=[generate_button])
        lighting_option.change(self._select_lighting_option, inputs=[lighting_option], outputs=[light_yaw, light_pitch])

        generate_button.click(self._process, inputs=[
            self.input_image,
            light_yaw,
            light_pitch,
            specular_power,
            normal_diffuse_strength,
            specular_highlights_strength,
            total_gain
        ], outputs=[output_image])

    def _select_lighting_option(self, select_option_index):
        if select_option_index == 0:
            # 光源:真上
            return [60, -60]
        if select_option_index == 1:
            # 光源:左斜め上
            return [40, -60]
        if select_option_index == 2:
            # 光源：右斜め上
            return [60, -40]
        if select_option_index == 3:
            # 光源：左横
            return [0, 0]
        if select_option_index == 4:
            # 光源：右横
            return [90, 0]
        if select_option_index == 5:
            # 光源：真下
            return [45, 0]

    def _process(self, input_image_path, light_yaw, light_pitch, specular_power, normal_diffuse_strength,
                 specular_highlights_strength, total_gain):
        # ライティング効果を適用するために関数を呼び出します
        output_tensor = self.apply_lighting_effects(
            to_tensor(Image.open(input_image_path)),
            light_yaw,
            light_pitch,
            specular_power,
            normal_diffuse_strength,
            specular_highlights_strength,
            total_gain
        )

        # テンソルから画像へ変換
        output_pil: Image = to_pil_image(output_tensor.squeeze(0))
        output_pil.save(self.app_config.make_output_path())
        return output_pil

    def apply_lighting_effects(self, input_tensor, light_yaw, light_pitch, specular_power, normal_diffuse_strength,
                               specular_highlights_strength, total_gain):
        # 元の次元数を記録する
        original_dim = input_tensor.dim()

        # 入力テンソルが最低でも4次元であることを保証する（バッチ次元がなければ追加する）
        if original_dim == 3:
            input_tensor = input_tensor.unsqueeze(0)  # バッチ次元を追加

        # 入力テンソルに3つ以上のチャンネルがある場合、追加のチャンネルをアルファと仮定し削除する
        if input_tensor.shape[1] > 3:
            input_tensor = input_tensor[:, :3, :, :]  # 最初の3チャンネルのみを保持

        # 入力テンソルを正規化して法線ベクトルを取得する
        normal_tensor = torch.nn.functional.normalize(input_tensor, dim=1)  # チャンネル次元に沿って正規化

        # 光の方向ベクトルを計算する
        light_direction = self.euler_to_vector(light_yaw, light_pitch, 0)
        light_direction = light_direction.to(input_tensor.device)  # 同じデバイスを保証する

        # 光の方向とカメラの方向を入力テンソルの次元に合わせて拡張する
        batch_size, _, height, width = input_tensor.shape
        light_direction = light_direction.view(1, 3, 1, 1).expand(batch_size, -1, height, width)
        camera_direction = torch.tensor([0, 0, 1], dtype=torch.float32, device=input_tensor.device)
        camera_direction = camera_direction.view(1, 3, 1, 1).expand(batch_size, -1, height, width)

        # 拡散成分を計算する
        diffuse = torch.sum(normal_tensor * light_direction, dim=1, keepdim=True)
        diffuse = torch.clamp(diffuse, 0, 1)

        # 鏡面成分を計算する
        half_vector = torch.nn.functional.normalize(light_direction + camera_direction, dim=1)
        specular = torch.sum(normal_tensor * half_vector, dim=1, keepdim=True)
        specular = torch.pow(torch.clamp(specular, 0, 1), specular_power)

        # 拡散成分と鏡面成分を組み合わせて、強度とゲインを適用する
        output_tensor = (diffuse * normal_diffuse_strength + specular * specular_highlights_strength) * total_gain
        output_tensor = output_tensor.squeeze(1)  # keepdim=Trueで追加されたチャンネル次元を削除

        # 初めに追加されたバッチ次元があれば削除する
        if original_dim == 3:
            output_tensor = output_tensor.squeeze(0)

        return output_tensor

    def euler_to_vector(self, yaw, pitch, roll):
        # オイラー角から方向ベクトルを計算
        yaw_rad = np.radians(yaw)
        pitch_rad = np.radians(pitch)
        roll_rad = np.radians(roll)

        cos_pitch = np.cos(pitch_rad)
        sin_pitch = np.sin(pitch_rad)
        cos_yaw = np.cos(yaw_rad)
        sin_yaw = np.sin(yaw_rad)

        direction = np.array([
            sin_yaw * cos_pitch,
            -sin_pitch,
            cos_yaw * cos_pitch
        ])
        return torch.from_numpy(direction).float()
