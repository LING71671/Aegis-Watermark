# Aegis (神盾) - 专业级隐形水印与数字签名工具 🛡️
### Professional Blind Watermarking & Digital Signature Tool

Aegis 是一款结合了 **频域盲水印 (Blind Watermarking)** 与 **RSA 数字签名** 技术的版权保护工具。它不仅能为图像及 PPTX 文档嵌入肉眼不可见的“视觉指纹”，还能加盖不可伪造的“数字印章”。

Aegis is a copyright protection tool combining **frequency domain blind watermarking** and **RSA digital signatures**. It embeds invisible "visual fingerprints" and attaches unforgable "digital stamps" to images and PPTX documents.

---

## 🌟 核心亮点 | Key Features

- **视觉水印技术 (Visual Watermarking)**: 不同于脆弱的文本编码，Aegis 嵌入的是视觉轮廓，对截图、压缩、翻拍具有极强的抗性。
- **RSA-4096 数字签名 (Digital Signature)**: 集成自签名证书体系，一键证明身份并确保文件“未被篡改”。
- **SHA-256 安全加固 (Security Hardening)**: 支持任意长度字符串密钥，杜绝暴力破解撞库。
- **交互式控制台 (Interactive CLI)**: 中英双语菜单，无需记忆复杂指令，像使用独立 App 一样简单。
- **全自动文档保护 (Automated PPTX Protection)**: 自动识别并保护 PPT 内部的所有高价值图像素材。

---

## 🚀 快速开始 | Quick Start

### 1. 安装
```bash
pip install aegis-watermark
```

### 2. 身份初始化 (首次使用)
运行 `aegis` -> 选择 **身份管理 (Identity)** -> 输入你的姓名和邮箱，生成专属的加密证书。

### 3. 运行模式
- **嵌入 (Embed)**: 处理文件时，系统会询问是否附加数字签名。
- **提取 (Extract)**: 系统将自动校验数字签名（身份与完整性）并提取盲水印。

---

## 🛠️ 技术栈 | Tech Stack

- **算法核心**: `blind-watermark` (DCT/DWT 变换)
- **安全保障**: `cryptography` (RSA-4096 / SHA-256 / X.509)
- **UI 引擎**: `Rich` & `questionary`
- **文件处理**: `OpenCV`, `Pillow`, `python-pptx`

---

## 🔒 安全建议

- **私钥保护**: 身份证书保存在本地 `.aegis_identity` 目录，请务必妥善保管。
- **三重防护**: 建议同时使用“视觉水印 + 字符串加密 + 数字签名”以获得最高级别的保护。

---
**Aegis - 为每一份智力成果披上隐形神盾。**
