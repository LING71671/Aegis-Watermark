import os
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
        return engine.extract(input_path, output_wm_path=output_wm_path)
