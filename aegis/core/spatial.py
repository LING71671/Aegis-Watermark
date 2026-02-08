from PIL import Image

class SpatialWatermarker:
    """
    空域 LSB (Least Significant Bit) 水印实现。
    仅用于教学演示，抗干扰能力弱（转码即丢失），但完全隐形。
    """
    def embed(self, input_path: str, output_path: str, text: str):
        # 这是一个极简实现的占位符，实际工程中通常不推荐用LSB保护重要版权
        # 这里仅作结构展示
        img = Image.open(input_path)
        # TODO: LSB encoding logic here
        img.save(output_path)
        print(f"[Info] Spatial LSB watermark embedded (Simulation) -> {output_path}")

    def extract(self, input_path: str):
        print(f"[Info] Spatial LSB watermark extracted (Simulation)")
        return "DEMO_TEXT"