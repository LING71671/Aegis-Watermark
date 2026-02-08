# Aegis (神盾) - 专业级隐形水印与数字签名工具 🛡️
### Professional Blind Watermarking & Digital Signature Tool

[![PyPI version](https://img.shields.io/pypi/v/aegis-watermark.svg)](https://pypi.org/project/aegis-watermark/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Aegis (神盾)** 是一款专为高价值数字内容设计的安全保护工具。它完美结合了 **DCT/DWT 频域盲水印** 技术与 **RSA-4096 数字签名** 体系，能够为图像、PDF 及 PPTX 文档披上一层“隐形且不可伪造”的防御外壳。

**Aegis** is a security tool designed for high-value digital content. It seamlessly combines **DCT/DWT frequency domain blind watermarking** with **RSA-4096 digital signatures**, providing an "invisible and unforgable" defense layer for images, PDFs, and PPTX documents.

**专业** 注：仅人工智能认为

**神盾** 注：人工智能起的名

---

## ✨ 核心特性 | Features

### 1. 深度盲水印 (Blind Watermarking)
- **肉眼不可见 (Invisible)**：水印嵌入在频域中，完全不影响原始文件的视觉质量。
- **强鲁棒性 (Robust)**：能够抵抗截图、裁剪、缩放、压缩、甚至手机翻拍等常见的攻击手段。
- **指纹式追踪 (Tracing)**：通过视觉轮廓提取，直观地证明版权归属。

### 2. RSA-4096 数字签名 (Digital Signature)
- **身份鉴别 (Identity)**：通过 X.509 标准证书一键证明发送者身份。
- **防篡改 (Anti-tamper)**：利用 SHA-256 算法确保文件自签署后未被修改。
- **不可抵赖性 (Non-repudiation)**：基于非对称加密技术，确保签名的法律效力。

### 3. 全自动文档保护 (Automated Protection)
- **智能识别 (Auto-sniff)**：自动识别文件类型（Image / PPTX / PDF），支持批量内部图像处理。
- **PPTX 深度加固**：一键保护演示文稿内所有的核心图片素材。

### 4. 极致交互体验 (Interactive CLI)
- **双语支持 (Bilingual)**：内置中英双语菜单，适应不同使用环境。
- **交互式向导**：无需记忆参数，通过简单的菜单选择即可完成所有复杂操作。

---

## 🚀 安装与配置 | Installation

### 环境要求
- Python 3.8+
- 系统已安装 OpenCV 环境依赖

### 安装方式
```bash
pip install aegis-watermark
```

---

## 🛠️ 使用说明 | Usage Guide

### 1. 启动程序
在终端直接输入 `aegis` 即可进入交互式菜单：
```bash
aegis
```

### 2. 身份初始化 (Identity Setup)
首次使用前，请先创建身份证书：
1. 运行 `aegis`。
2. 选择 **身份管理 (Identity)**。
3. 输入你的姓名（或机构名）和邮箱。
4. 系统将在 `.aegis_identity/` 目录生成你的 RSA 密钥对。**请务必妥善保管私钥！**

### 3. 嵌入水印 (Embedding)
1. 选择 **嵌入水印 (Embed)**。
2. 输入待处理的文件路径。
3. 输入水印文本（例如：“© 2026 LING”）。
4. 设置一个**自定义密钥**（用于加强盲水印的安全性，提取时需对应）。
5. 若已设置身份，可选择“附加数字签名”。

### 4. 提取与核验 (Extraction & Verification)
1. 选择 **提取分析 (Extract)**。
2. 输入文件路径和密钥。
3. 系统将展示**分析报告**：
   - **数字签名状态**：显示签署人及完整性核验结果。
   - **水印证据**：生成一份包含提取出的水印轮廓的证据图片。

---

## 💡 命令行模式 | CLI Mode

如果您需要集成到脚本中，也可以使用命令参数模式：

```bash
# 嵌入模式
aegis embed -i original.png -o output.png -t "WATERMARK" -k "YOUR_KEY"

# 提取模式
aegis extract -i output.png -o evidence.png -k "YOUR_KEY"
```

---

## 🏗️ 项目架构 | Architecture

- `aegis/core/`: 核心算法逻辑（DCT/DWT 变换、RSA 签名管理、文件指纹嗅探）。
- `aegis/handlers/`: 文件处理器（针对 Image、PDF、PPTX 的特定读写逻辑）。
- `aegis/cli.py`: 交互式菜单与命令行入口。

---

## ⚖️ 开源协议 | License

本项目采用 [MIT License](LICENSE) 开源。

---
**Aegis - 为每一份智力成果披上隐形神盾。**
**Protecting your intellectual property with invisible shields.**
