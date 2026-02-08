import fitz  # PyMuPDF
import os
import cv2
import numpy as np
from PIL import Image
from aegis.handlers.base import BaseHandler
from aegis.core.frequency import FrequencyWatermarker

class PDFHandler(BaseHandler):
    def process(self, input_path, output_path, watermark_text, key="1"):
        """
        处理 PDF: 将每一页渲染为图像，嵌入盲水印，最后合并
        """
        print(f"[*] Processing PDF: {input_path}")
        try:
            doc = fitz.open(input_path)
            engine = FrequencyWatermarker(key=key)
            
            # 创建一个临时的 PDF 用于存储带水印的页面
            output_doc = fitz.open()
            
            for page_index in range(len(doc)):
                page = doc[page_index]
                # 将 PDF 页面渲染为高分辨率图片 (zoom=2.0 提高清晰度)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # 转为 numpy 数组 (RGB)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # 临时保存渲染图
                temp_page_img = f"temp_page_{page_index}.png"
                temp_protected_img = f"temp_prot_{page_index}.png"
                cv2.imwrite(temp_page_img, img)
                
                # 嵌入水印
                success = engine.embed(temp_page_img, temp_protected_img, watermark_text)
                
                if success:
                    # 将带水印的图片插回新 PDF
                    img_doc = fitz.open(temp_protected_img)
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_pdf = fitz.open("pdf", pdf_bytes)
                    output_doc.insert_pdf(img_pdf)
                    img_doc.close()
                
                # 清理临时文件
                if os.path.exists(temp_page_img): os.remove(temp_page_img)
                if os.path.exists(temp_protected_img): os.remove(temp_protected_img)

            output_doc.save(output_path)
            output_doc.close()
            doc.close()
            return True
        except Exception as e:
            print(f"[!] PDF Processing Error: {e}")
            return False

    def extract(self, input_path, output_wm_path=None, key="1"):
        """
        从 PDF 提取: 默认提取第一页的水印作为证据
        """
        print(f"[*] Extracting from PDF (First Page): {input_path}")
        try:
            doc = fitz.open(input_path)
            if len(doc) == 0: return None
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            temp_extract_img = "temp_for_extract.png"
            cv2.imwrite(temp_extract_img, img)
            
            engine = FrequencyWatermarker(key=key)
            wm_size = engine.get_safe_wm_size(img.shape)
            result = engine.extract(temp_extract_img, wm_size, output_wm_path=output_wm_path)
            
            if os.path.exists(temp_extract_img): os.remove(temp_extract_img)
            doc.close()
            return result
        except Exception as e:
            print(f"[!] PDF Extraction Error: {e}")
            return None
