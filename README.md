# Aegis - 隐形水印与数字签名工具 🛡️
### Blind Watermarking & Digital Signature Tool

[![PyPI version](https://img.shields.io/pypi/v/aegis-watermark.svg)](https://pypi.org/project/aegis-watermark/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aegis 是一个用于图片、PDF 及 PPTX 文档的盲水印嵌入与数字签名工具。它通过频域算法实现隐形版权标记，并结合 RSA 技术提供文件完整性校验。

Aegis is a tool for embedding blind watermarks and digital signatures into images, PDFs, and PPTX documents. It uses frequency-domain algorithms for invisible copyright marking and RSA technology for file integrity verification.

---

## ✨ 主要功能 | Features

- **隐形盲水印 (Blind Watermarking)**：在频域嵌入不可见的水印，支持图片和 PDF 全页面保护，具有一定的抗压缩和抗裁剪能力。
- **数字签名 (Digital Signature)**：支持 RSA-4096 签名，用于验证文件签署人身份及文件是否被篡改。
- **文档支持 (Doc Support)**：支持对 PPTX 内部图片进行批量保护，以及对 PDF 页面进行整体水印覆盖。
- **交互式命令行 (CLI)**：提供简单易用的中英双语交互菜单。

---

## 🚀 快速开始 | Quick Start

### 安装
```bash
pip install aegis-watermark
```

### 使用
在终端输入 `aegis` 即可进入交互菜单：
```bash
aegis
```

1. **身份管理 (Identity)**：首次使用请先创建身份证书（保存在本地 `.aegis_identity/`）。
2. **嵌入 (Embed)**：选择文件并输入水印内容。
3. **提取 (Extract)**：输入带水印的文件，系统将分析并输出水印证据图。

---

## ⚠️ 注意事项 | Troubleshooting

1. **密钥一致性**: 提取时必须使用与嵌入时相同的密钥。
2. **尺寸敏感**: 盲水印对大幅度的非等比例缩放或过度裁剪较为敏感。
3. **压缩强度**: 极低质量的有损压缩可能会破坏水印信号。

---

## 💡 命令行模式 | CLI Mode

```bash
# 嵌入
aegis embed -i in.png -o out.png -t "WM" -k "key"

# 提取
aegis extract -i out.png -o evidence.png -k "key"
```

---

## ⚖️ 开源协议 | License

本项目采用 [MIT License](LICENSE) 开源。