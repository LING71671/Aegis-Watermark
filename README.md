# Aegis - 隐形水印与数字签名工具
### Blind Watermarking & Digital Signature Tool

[![PyPI version](https://img.shields.io/pypi/v/aegis-watermark.svg)](https://pypi.org/project/aegis-watermark/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Aegis 是一个简单的开源工具，用于在图片、PDF 及 PPTX 文档中嵌入盲水印和数字签名。它通过频域算法提供基础的版权标记功能，并利用 RSA 技术协助验证文件的来源与完整性。

Aegis is a simple open-source tool for embedding blind watermarks and digital signatures into images, PDFs, and PPTX documents. It provides basic copyright marking using frequency-domain algorithms and helps verify file source and integrity via RSA technology.

---

## 主要功能 | Features

- **基础盲水印**: 支持在图片和 PDF 页面中嵌入不影响视觉质量的隐形标记，具备基础的抗压缩能力。
- **数字签名**: 支持生成多套 RSA-4096 密钥对，为文件提供可追溯的数字签署。
- **文档分发与溯源**: 集成了简单的邮件分发流程和本地 SQLite 数据库，用于记录文件的分发去向，协助在发现泄露时进行初步溯源。
- **自动化操作**: 提供交互式引导界面，支持自动生成建议的文件保存路径及提取后的自动预览。

---

## 安装与环境配置 | Installation & Setup

### 1. 环境准备
在安装 Aegis 之前，建议确保您的系统已具备以下基础环境：

- **Python 3.8+**: 推荐从 [Python 官网](https://www.python.org/downloads/) 下载。
- **OpenCV 运行库**: 底层图像处理依赖。通常通过 `pip` 自动安装，若在特殊 Linux 环境下运行，请参考相关发行版的包管理说明。

### 2. 安装 Aegis
```bash
pip install aegis-watermark
```

---

## 使用教程 | Usage Guide

### 1. 快速进入界面
直接在终端输入以下命令即可打开交互式菜单，无需记忆复杂的参数：
```bash
aegis
```

### 2. 身份与配置 (Settings)
首次使用前，建议完成以下设置：
- **身份证书**: 支持创建多个身份。例如可以分别为“个人”和“工作”创建不同的 RSA 证书。
- **发信配置**: 如果需要使用批量分发功能，请在此处配置 SMTP 邮箱信息。

### 3. 版权保护与追踪 (Workflow)
- **嵌入 (Embed)**: 选择文件并输入水印文本。若有多套身份，系统会提示您选择签署者。
- **分发 (Distribute)**: 准备一个包含邮箱列表的文本文件，系统将为每位收件人生成带唯一 ID 的副本并通过邮件发送。
- **溯源 (Trace)**: 发现疑似泄露文件时，使用此功能提取 ID，系统将自动检索本地数据库返回分发记录。

### 4. 交互小技巧
- **回退**: 在输入任何路径或文本时，输入 `:b` 即可随时放弃当前操作并返回主菜单。
- **编辑**: 支持使用键盘方向键对已输入的文字进行移动和修改。

---

## 注意事项 | Troubleshooting

- **算法局限性**: 盲水印技术在面对极高强度的破坏性压缩或大幅度拉伸时，提取效果可能会下降。
- **存储建议**: 私钥和追踪数据库保存在本地 `.aegis_identity/` 目录，请注意备份与安全。

---

## 开源协议 | License

本项目采用 [GPL v3](LICENSE) 协议开源。
