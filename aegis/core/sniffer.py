import os

def sniff_file_type(file_path):
    """
    通过读取文件头 Magic Number 识别文件真实类型。
    返回: 'image', 'ppt', 'unknown'
    """
    if not os.path.exists(file_path):
        return 'unknown'
        
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            
        # 1. 检查图片特征
        # PNG: 89 50 4E 47
        # JPEG: FF D8 FF
        if header.startswith(b'\x89PNG') or header.startswith(b'\xff\xd8\xff'):
            return 'image'
            
        # 2. 检查 ZIP 特征 (PPTX 本质是 ZIP)
        # PK.. : 50 4B 03 04
        if header.startswith(b'PK\x03\x04'):
            return 'ppt'
            
        # 3. 检查 PDF 特征
        # %PDF- : 25 50 44 46 2D
        if header.startswith(b'%PDF-'):
            return 'pdf'
            
        return 'unknown'
    except:
        return 'unknown'
