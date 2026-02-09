import os
import cv2
from aegis.core.frequency import FrequencyWatermarker
from aegis.handlers.base import BaseHandler

class ImageHandler(BaseHandler):
    def process(self, input_path, output_path, watermark_text, key="1"):
        """处理单张图片 - 引入 2K 标准化缩放提升平铺容量"""
        print(f"[*] Processing Image (High-Res Mode): {input_path}")
        img = cv2.imread(input_path)
        if img is None: return False
        
        # 统一缩放到 2000px 宽度以获得一致的平铺密度
        target_w = 2000
        target_h = int(img.shape[0] * (target_w / img.shape[1]))
        img_resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        # 临时保存缩放后的图进行嵌入
        temp_input = f"temp_in_{os.path.basename(input_path)}"
        cv2.imwrite(temp_input, img_resized)
        
        engine = FrequencyWatermarker(key=key)
        # 使用 12 的平衡强度
        success = engine.embed(temp_input, output_path, watermark_text, intensity=12)
        
        if os.path.exists(temp_input): os.remove(temp_input)
        return success

    def extract(self, input_path, output_wm_path=None, key="1"):
        """从单张图片提取 - 同样执行 2K 采样与中值去噪"""
        print(f"[*] Extracting from Image (High-Res Mode): {input_path}")
        img = cv2.imread(input_path)
        if img is None: return None
        
        # 必须缩放到嵌入时相同的 2000px 宽度
        target_w = 2000
        target_h = int(img.shape[0] * (target_w / img.shape[1]))
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        # 中值滤波去噪，消除图片压缩产生的椒盐噪声
        img = cv2.medianBlur(img, 3)
        
        temp_extract_img = "temp_for_extract_img.png"
        cv2.imwrite(temp_extract_img, img)
        
        engine = FrequencyWatermarker(key=key)
        wm_size = engine.get_safe_wm_size(img.shape)
        result = engine.extract(temp_extract_img, wm_size, output_wm_path=output_wm_path)
        
        if os.path.exists(temp_extract_img): os.remove(temp_extract_img)
        return result
