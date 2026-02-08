import json
import os

class BaseHandler:
    """
    所有文件处理器的基类，提供通用的数字签名附加与提取功能。
    """
    def attach_signature(self, file_path, sig_mgr):
        """将数字签名追加到文件物理末尾"""
        try:
            # 1. 读取当前文件内容（签署的是当前状态）
            with open(file_path, "rb") as f:
                original_content = f.read()

            # 2. 生成签名包
            sig_b64, cert_pem = sig_mgr.sign_file(file_path)
            sig_bundle = {
                "sig": sig_b64,
                "cert": cert_pem
            }
            sig_data = json.dumps(sig_bundle).encode('utf-8')

            # 3. 追加到文件末尾: [原始数据] + [边界符] + [签名JSON]
            with open(file_path, "ab") as f:
                f.write(sig_mgr.SIG_BOUNDARY)
                f.write(sig_data)
            return True
        except Exception as e:
            print(f"[Debug] Failed to attach signature: {e}")
            return False

    def get_signature(self, file_path, sig_mgr):
        """从文件末尾提取并验证签名"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            
            # 1. 寻找边界符
            if sig_mgr.SIG_BOUNDARY not in content:
                return "none", None

            # 2. 切分数据
            parts = content.split(sig_mgr.SIG_BOUNDARY)
            # 取最后一个边界符之后的数据作为签名包，边界符之前的所有数据作为原始载体
            # 这样即使文件本身包含类似边界符的字节（极罕见），也能保证逻辑健壮
            sig_json_bytes = parts[-1]
            original_bytes = sig_mgr.SIG_BOUNDARY.join(parts[:-1])
            
            # 3. 解析并验证
            sig_bundle = json.loads(sig_json_bytes.decode('utf-8'))
            valid, info = sig_mgr.verify_signature(original_bytes, sig_bundle["sig"], sig_bundle["cert"])
            return ("valid" if valid else "invalid"), info
            
        except Exception as e:
            print(f"[Debug] Verify error: {e}")
            return "none", None
