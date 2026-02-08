import os
import cv2
import hashlib
import numpy as np
import uuid
from PIL import Image, ImageDraw, ImageFont
import blind_watermark
from blind_watermark import WaterMark

blind_watermark.bw_notes.close()

class FrequencyWatermarker:
    def __init__(self, key: str = "1"):
        hash_digest = hashlib.sha256(str(key).encode()).digest()
        seed = int.from_bytes(hash_digest[:8], 'big') % (2**32)
        self.pwd_wm = seed
        self.pwd_img = seed

    def get_safe_wm_size(self, img_shape):
        h, w = img_shape[:2]
        side = min(h // 8, w // 8)
        side = (side // 2) * 2
        return (side, side)

    def pre_generate_wm(self, text, size):
        """主进程预生成水印图，避免子进程重复开销"""
        img = Image.new('1', size, 0)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size[0] - tw) // 2, (size[1] - th) // 2), text, font=font, fill=1)
        
        path = f"temp_master_wm_{uuid.uuid4().hex}.png"
        img.save(path)
        return path

    def embed_with_precomputed_wm(self, input_path, output_path, wm_path, intensity=5):
        """子进程专用的轻量化嵌入函数"""
        try:
            bwm = WaterMark(password_wm=self.pwd_wm, password_img=self.pwd_img, block_shape=(8, 8))
            if hasattr(bwm, 'd1'): bwm.d1 = intensity
            if hasattr(bwm, 'd2'): bwm.d2 = intensity
            
            bwm.read_img(input_path)
            bwm.read_wm(wm_path)
            bwm.embed(output_path)
            return True
        except:
            return False

    def extract(self, input_path, wm_size, output_wm_path=None):
        """增强版提取，支持传入明确的 wm_size"""
        if output_wm_path is None: output_wm_path = input_path + "_wm.png"
        try:
            bwm = WaterMark(password_wm=self.pwd_wm, password_img=self.pwd_img, block_shape=(8, 8))
            bwm.extract(input_path, wm_shape=wm_size, out_wm_name=output_wm_path, mode='img')
            return output_wm_path
        except:
            return ""