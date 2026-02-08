import os
import cv2
from aegis.core.frequency import FrequencyWatermarker
from aegis.handlers.base import BaseHandler

class ImageHandler(BaseHandler):
    def process(self, input_path, output_path, watermark_text, key="1"):
        """处理单张图片"""
        print(f"[*] Processing Image: {input_path}")
        engine = FrequencyWatermarker(key=key)
        return engine.embed(input_path, output_path, watermark_text)

    def extract(self, input_path, output_wm_path=None, key="1"):
        """从单张图片提取"""
        print(f"[*] Extracting from Image: {input_path}")
        engine = FrequencyWatermarker(key=key)
        
        # 提取前需要计算水印可能的尺寸
        img = cv2.imread(input_path)
        if img is None: return None
        wm_size = engine.get_safe_wm_size(img.shape)
        
        return engine.extract(input_path, wm_size, output_wm_path=output_wm_path)
