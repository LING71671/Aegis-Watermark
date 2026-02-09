from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aegis-watermark',
    version='0.3.0',
    author='LingQingyang',
    author_email='1739677116@qq.com',
    description='图片与PPT专业级隐形盲水印工具 | Professional blind watermarking tool for images and PPTX documents.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/LING71671/Aegis-Watermark',
    packages=find_packages(),
    install_requires=[
        'blind-watermark',
        'opencv-python',
        'numpy<2.0.0',
        'click',
        'Pillow',
        'pyfiglet',
        'rich',
        'python-pptx',
        'questionary',
        'cryptography',
        'pymupdf'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'aegis=aegis.cli:main',
        ],
    },
)