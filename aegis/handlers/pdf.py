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
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        unique_id = uuid.uuid4().hex
        temp_page_img = f"temp_page_{page_index}_{unique_id}.png"
        temp_protected_img = f"temp_prot_{page_index}_{unique_id}.png"
        cv2.imwrite(temp_page_img, img)
        
        engine = FrequencyWatermarker(key=key)
        success = engine.embed(temp_page_img, temp_protected_img, watermark_text)
        
        pdf_bytes = None
        if success:
            img_doc = fitz.open(temp_protected_img)
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()
            
        # 清理
        if os.path.exists(temp_page_img): os.remove(temp_page_img)
        if os.path.exists(temp_protected_img): os.remove(temp_protected_img)
        doc.close()
        
        return page_index, pdf_bytes
    except Exception as e:
        print(f"[!] Error processing page {page_index}: {e}")
        return page_index, None

class PDFHandler(BaseHandler):
    def process(self, input_path, output_path, watermark_text, key="1"):
        """
        并行处理 PDF: 利用多进程加速页面渲染与水印嵌入
        """
        print(f"[*] Processing PDF (Parallel Mode): {input_path}")
        try:
            doc = fitz.open(input_path)
            num_pages = len(doc)
            doc.close() # 进程池内会重新打开
            
            # 准备并行任务参数
            tasks = [(i, input_path, watermark_text, key) for i in range(num_pages)]
            
            # 使用进程池执行
            # 注：在 Windows 下，必须确保代码在 if __name__ == "__main__" 下运行，
            # 但作为库调用时，这里由调用的主进程保证。
            results = []
            with ProcessPoolExecutor() as executor:
                results = list(executor.map(process_single_page, tasks))
            
            # 按页码排序合并结果
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
            print(f"[!] PDF Parallel Processing Error: {e}")
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
