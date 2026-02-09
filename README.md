# Aegis - 隐形水印与数字签名工具 🛡️
### Blind Watermarking & Digital Signature Tool

[![PyPI version](https://img.shields.io/pypi/v/aegis-watermark.svg)](https://pypi.org/project/aegis-watermark/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Aegis 是一个用于图片、PDF 及 PPTX 文档的盲水印嵌入与数字签名工具。它采用 GPLv3 协议开源，确保自由软件的持续传承。

Aegis is a tool for embedding blind watermarks and digital signatures into images, PDFs, and PPTX documents. It uses frequency-domain algorithms for invisible copyright marking and RSA technology for file integrity verification.

---

## ✨ 主要功能 | Features

- **隐形盲水印 (Blind Watermarking)**：在频域嵌入不可见的水印，支持全页面保护，具有抗压缩和抗裁剪能力。
- **数字签名 (Digital Signature)**：支持 RSA-4096 签名，用于验证文件签署人身份及文件是否被篡改。
- **文档支持 (Doc Support)**：支持对 PPTX 内部图片进行批量保护，以及对 PDF 页面进行整体水印覆盖。
- **并行处理 (Parallel Processing)**：针对多页 PDF 提供多进程并行加速。

---

## 🚀 安装与环境配置 | Installation & Setup

### 1. 环境准备
在安装 Aegis 之前，请确保您的系统已具备以下基础环境：

- **Python 3.8+**: 推荐从 [Python 官网](https://www.python.org/downloads/) 下载。如需指导，可参考 [官方安装指南](https://docs.python.org/zh-cn/3/using/index.html)。
- **OpenCV 运行库**: 本工具依赖 OpenCV 进行底层图像处理。通常 `pip` 会自动处理相关依赖，但在某些特定环境下，您可能需要参考 [OpenCV 官方文档](https://docs.opencv.org/master/da/df6/tutorial_py_abs_installation.html) 手动配置环境。

### 2. 安装 Aegis
在终端执行以下命令即可一键安装：

```bash
pip install aegis-watermark
```

---

## 🛠️ 详细使用指南 | Detailed Usage Guide

Aegis 提供交互式菜单与命令行参数两种使用方式。

### 1. 身份初始化 (Identity Setup)
在使用数字签名功能前，需要先建立身份：
- 运行 `aegis` 并选择 **身份管理 (Identity)**。
- 输入姓名（或机构名）与邮箱，系统将生成 RSA-4096 密钥对及证书。
- **安全提示**：私钥保存在本地 `.aegis_identity/` 目录，请务必妥善保管。

### 2. 交互模式 (Interactive Mode)
直接在终端输入 `aegis` 即可进入向导：
1. **嵌入水印 (Embed)**：
   - 输入文件路径（图片、PDF 或 PPTX）。
   - 输入水印文本。
   - 设置**密钥 (Key)**：这是提取水印的唯一凭证，建议使用复杂的字符串。
   - 若已初始化身份，可选择是否附加数字签名。
2. **提取分析 (Extract)**：
   - 输入带水印的文件路径。
   - 输入嵌入时使用的密钥。
   - 系统将生成分析报告，并输出水印证据图片。

### 3. 命令行模式 (CLI Mode)
适用于脚本自动化处理：
```bash
# 嵌入水印
# -i: 输入文件, -o: 输出文件, -t: 水印内容, -k: 密钥
aegis embed -i original.jpg -o protected.jpg -t "Copyright-2026" -k "MySecretKey"

# 提取水印
# -i: 输入文件, -o: 证据图保存路径, -k: 密钥
aegis extract -i protected.jpg -o evidence.png -k "MySecretKey"
```

### 4. 特定格式说明 (Format Specifics)
- **PDF**: 采用全页面平铺水印与 2K 超采样渲染，确保复杂背景下的提取清晰度。
- **PPTX**: 自动遍历演示文稿中的所有幻灯片，对其中嵌入的图片进行盲水印保护。

---

## ⚠️ 注意事项 | Troubleshooting

- **提取乱码**: 盲水印对**密钥**极其敏感，提取时若密钥错误将得到乱码。此外，若图像比例被严重拉伸，提取效果也会受到影响。
- **文件体积**: PDF 处理后由于采用了图像化保护，文件体积会有所增加。
- **数字签名**: 若文件在签署后被第三方软件（如 Photoshop）修改并另存为，数字签名可能会失效。

---

## ⚖️ 开源协议 | License

本项目采用 [MIT License](LICENSE) 开源。
