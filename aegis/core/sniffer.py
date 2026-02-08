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
            # 进一步确认是否包含 ppt/ 目录特征 (简单判断)
            # 这里为保持轻量不深入解压，通常 PK 开头的我们就尝试以 PPT/Zip 处理
            return 'ppt'
            
        return 'unknown'
    except:
        return 'unknown'
