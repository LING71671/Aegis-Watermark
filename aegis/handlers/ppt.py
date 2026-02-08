import os
import zipfile
import shutil
import tempfile
import json
from aegis.core.frequency import FrequencyWatermarker
from aegis.handlers.base import BaseHandler

class PPTHandler(BaseHandler):
    """
    PPTX 处理器：将 PPTX 视为 ZIP 解压，处理内部 media 目录下的图片。
    支持加密（Embed）和解密验证（Extract）。
    """
    def __init__(self):
        # 忽略小图标、缩略图，避免破坏UI (单位: 字节)
        self.min_file_size = 50 * 1024  # 50KB

    def process(self, input_path, output_path, watermark_text, key="1"):
        """给 PPTX 打水印"""
        print(f"[*] Processing PPTX: {input_path}")
        engine = FrequencyWatermarker(key=key)

        # 创建临时工作目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. 解压 PPTX
            try:
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile:
                print(f"[Error] Not a valid PPTX/Zip file: {input_path}")
                return False

            # 2. 遍历 ppt/media/ 目录
            media_dir = os.path.join(temp_dir, 'ppt', 'media')
            if os.path.exists(media_dir):
                for filename in os.listdir(media_dir):
                    file_path = os.path.join(media_dir, filename)

                    # 检查是否为图片且大小足够
                    if self._is_target_image(filename) and os.path.getsize(file_path) > self.min_file_size:
                        print(f"    -> Watermarking inner image: {filename}")
                        # 原地替换：读取原图 -> 加水印 -> 覆盖原图
                        temp_img = file_path + ".tmp.png"
                        success = engine.embed(file_path, temp_img, watermark_text)
                        if success:
                            os.replace(temp_img, file_path)
                        else:
                            if os.path.exists(temp_img): os.remove(temp_img)

            # 3. 重新打包 (Re-zip)
            self._zip_folder(temp_dir, output_path)
            print(f"[+] Success! Protected PPT saved to: {output_path}")
            return True

    def extract(self, input_path, key="1"):
        """
        从 PPTX 中提取水印。
        """
        print(f"[*] Extracting from PPTX: {input_path}")
        engine = FrequencyWatermarker(key=key)

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile:
                return "Error: Invalid PPTX file"

            media_dir = os.path.join(temp_dir, 'ppt', 'media')
            if not os.path.exists(media_dir):
                return "No media found in PPTX"

            # 遍历图片
            image_files = [f for f in os.listdir(media_dir) if self._is_target_image(f)]
            total_imgs = len(image_files)
            print(f"    -> Found {total_imgs} images. Scanning candidates (>50KB)...")

            for filename in image_files:
                file_path = os.path.join(media_dir, filename)
                # 只检测大图，提高效率且排除干扰
                if os.path.getsize(file_path) > self.min_file_size:
                    # 尝试提取
                    output_name = os.path.basename(input_path) + "_extracted_wm.png"
                    wm_path = engine.extract(file_path, output_wm_path=output_name)
                    if wm_path and os.path.exists(wm_path):
                        print(f"    -> Found trace in {filename}. Saved to: {wm_path}")
                        return wm_path

        return "No watermark detected"

    def _is_target_image(self, filename):
        ext = filename.lower().split('.')[-1]
        return ext in ['png', 'jpg', 'jpeg', 'bmp', 'tiff']

    def _zip_folder(self, folder_path, output_path):
        """将文件夹重新打包为 ZIP/PPTX"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder_path)
                    zip_ref.write(full_path, rel_path)
