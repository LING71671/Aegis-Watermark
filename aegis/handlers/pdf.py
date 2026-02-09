import fitz  # PyMuPDF
import os
import cv2
import numpy as np
import uuid
from concurrent.futures import ProcessPoolExecutor
from aegis.handlers.base import BaseHandler
from aegis.core.frequency import FrequencyWatermarker

def process_single_page(page_data):
    """
    独立函数，用于多进程并行调用。
    """
    page_index, pdf_path, watermark_text, key = page_data
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_index]
        # 提高 DPI 以获得超采样效果
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # 统一缩放到 2000px 宽度
        target_w = 2000
        target_h = int(img.shape[0] * (target_w / img.shape[1]))
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        unique_id = uuid.uuid4().hex
        temp_page_img = f"temp_page_{page_index}_{unique_id}.png"
        temp_protected_img = f"temp_prot_{page_index}_{unique_id}.png"
        cv2.imwrite(temp_page_img, img)
        
        engine = FrequencyWatermarker(key=key)
        # 使用平衡强度
        success = engine.embed(temp_page_img, temp_protected_img, watermark_text, intensity=12)
        
        pdf_bytes = None
        if success:
            img_doc = fitz.open(temp_protected_img)
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()
            
        if os.path.exists(temp_page_img): os.remove(temp_page_img)
        if os.path.exists(temp_protected_img): os.remove(temp_protected_img)
        doc.close()
        
        return page_index, pdf_bytes
    except Exception as e:
        print(f"[ERROR] Page processing exception {page_index}: {e}")
        return page_index, None

class PDFHandler(BaseHandler):
    def process(self, input_path, output_path, watermark_text, key="1"):
        """
        并行处理 PDF: 利用多进程加速页面渲染与水印嵌入
        """
        print(f"[*] Processing PDF (High-Res Mode): {input_path}")
        try:
            doc = fitz.open(input_path)
            num_pages = len(doc)
            doc.close()
            
            tasks = [(i, input_path, watermark_text, key) for i in range(num_pages)]
            
            results = []
            with ProcessPoolExecutor() as executor:
                results = list(executor.map(process_single_page, tasks))
            
            results.sort(key=lambda x: x[0])
            
            output_doc = fitz.open()
            for _, pdf_bytes in results:
                if pdf_bytes:
                    img_pdf = fitz.open("pdf", pdf_bytes)
                    output_doc.insert_pdf(img_pdf)
                    img_pdf.close()
            
            output_doc.save(output_path)
            output_doc.close()
            return True
        except Exception as e:
            print(f"[ERROR] PDF processing exception: {e}")
            return False

    def extract(self, input_path, output_wm_path=None, key="1"):
        """
        从 PDF 提取: 2000px 采样 + 中值滤波去噪
        """
        print(f"[*] Extracting from PDF (High-Res Mode): {input_path}")
        try:
            doc = fitz.open(input_path)
            if len(doc) == 0: return None
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            target_w = 2000
            target_h = int(img.shape[0] * (target_w / img.shape[1]))
            img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            # 使用中值滤波去除 DCT 带来的块状噪声 (椒盐噪声)
            img = cv2.medianBlur(img, 3)
            
            temp_extract_img = "temp_for_extract.png"
            cv2.imwrite(temp_extract_img, img)
            
            engine = FrequencyWatermarker(key=key)
            wm_size = engine.get_safe_wm_size(img.shape)
            result = engine.extract(temp_extract_img, wm_size, output_wm_path=output_wm_path)
            
            if os.path.exists(temp_extract_img): os.remove(temp_extract_img)
            doc.close()
            return result
        except Exception as e:
            print(f"[ERROR] PDF extraction exception: {e}")
            return None
