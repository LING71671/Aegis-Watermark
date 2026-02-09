import os
import datetime
import hashlib
import json
import base64
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

class SignatureManager:
    """
    数字签名管理器：负责 RSA 密钥对、自签名证书的生成、签署与验证。
    """
    SIG_BOUNDARY = b"\x00--AEGIS-SIGNATURE-DATA--"

    def __init__(self, keys_dir=".aegis_identity"):
        # 默认存储身份信息的目录（建议放在用户家目录，这里暂设在项目内）
        self.keys_dir = os.path.abspath(keys_dir)
        self.priv_path = os.path.join(self.keys_dir, "private.key")
        self.cert_path = os.path.join(self.keys_dir, "identity.crt")
        
        if not os.path.exists(self.keys_dir):
            os.makedirs(self.keys_dir)

    def has_identity(self):
        """检查是否存在至少一个身份"""
        if not os.path.exists(self.keys_dir): return False
        return len(self.list_identities()) > 0

    def list_identities(self):
        """列出所有可用身份"""
        identities = []
        if not os.path.exists(self.keys_dir): return []
        
        for f in os.listdir(self.keys_dir):
            if f.endswith(".crt"):
                ident_id = f.replace("identity", "").replace(".crt", "").strip("_")
                if not ident_id: ident_id = "default"
                identities.append(ident_id)
        return sorted(identities)

    def create_identity(self, name, email, ident_id=None):
        """
        创建 RSA 4096 位密钥及自签名 X.509 证书。
        支持多身份ID，不覆盖默认身份。
        """
        suffix = f"_{ident_id}" if ident_id else ""
        priv_name = f"private{suffix}.key"
        cert_name = f"identity{suffix}.crt"
        
        priv_path = os.path.join(self.keys_dir, priv_name)
        cert_path = os.path.join(self.keys_dir, cert_name)

        # 1. 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        # 2. 生成证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Aegis Protection"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365*20)
        ).sign(private_key, hashes.SHA256(), default_backend())

        # 3. 保存到本地
        with open(priv_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        return cert_path

    def sign_file(self, file_path, ident_id=None):
        """
        对文件进行数字签署。
        """
        if not self.has_identity():
            raise Exception("No identity found.")

        suffix = f"_{ident_id}" if ident_id and ident_id != "default" else ""
        priv_path = os.path.join(self.keys_dir, f"private{suffix}.key")
        cert_path = os.path.join(self.keys_dir, f"identity{suffix}.crt")
        
        if not os.path.exists(priv_path):
            # Fallback to default if specified ID not found
            priv_path = self.priv_path
            cert_path = self.cert_path

        # 读取私钥
        with open(priv_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

        # 读取证书
        with open(cert_path, "rb") as f:
            cert_pem = f.read().decode('utf-8')

        # 计算文件哈希 (SHA-256)
        file_hash = self._calculate_hash(file_path)

        # 进行签名
        signature = private_key.sign(
            file_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        sig_b64 = base64.b64encode(signature).decode('utf-8')
        return sig_b64, cert_pem

    def verify_signature(self, file_bytes_without_sig, sig_b64, cert_pem=None):
        """
        验证签名。如果 cert_pem 为空，则轮询本地所有证书。
        """
        try:
            public_key = None
            info = None
            
            # 策略 A: 使用传入的证书 (自包含模式)
            if cert_pem:
                cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
                public_key = cert.public_key()
                subject = cert.subject
                info = {
                    "name": subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
                    "email": subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value,
                    "expiry": cert.not_valid_after.strftime("%Y-%m-%d")
                }
            
            # 策略 B: 轮询本地证书 (如果文件里没带证书，或者为了强校验)
            else:
                for ident_id in self.list_identities():
                    suffix = f"_{ident_id}" if ident_id != "default" else ""
                    c_path = os.path.join(self.keys_dir, f"identity{suffix}.crt")
                    try:
                        with open(c_path, "rb") as f:
                            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
                            # 尝试验证
                            signature = base64.b64decode(sig_b64)
                            file_hash = hashlib.sha256(file_bytes_without_sig).digest()
                            cert.public_key().verify(
                                signature,
                                file_hash,
                                padding.PSS(
                                    mgf=padding.MGF1(hashes.SHA256()),
                                    salt_length=padding.PSS.MAX_LENGTH
                                ),
                                hashes.SHA256()
                            )
                            # 验证通过，提取信息
                            public_key = cert.public_key()
                            subject = cert.subject
                            info = {
                                "name": subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
                                "email": subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value,
                                "expiry": cert.not_valid_after.strftime("%Y-%m-%d")
                            }
                            break
                    except:
                        continue
            
            if not public_key: return False, None

            # 二次确认 (如果是策略 A，这里才真正验签)
            if cert_pem:
                file_hash = hashlib.sha256(file_bytes_without_sig).digest()
                signature = base64.b64decode(sig_b64)
                public_key.verify(
                    signature,
                    file_hash,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            
            return True, info
        except Exception as e:
            # print(f"[Debug] Verify Failed: {e}")
            return False, None

    def _calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.digest()
