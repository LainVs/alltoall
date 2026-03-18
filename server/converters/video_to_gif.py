import subprocess
import os
from .base import BaseConverter

class VideoToGifConverter(BaseConverter):
    def __init__(self, source_ext, target_ext=".gif"):
        self._source_ext = source_ext
        self._target_ext = target_ext

    @property
    def supported_extension(self):
        return self._source_ext

    @property
    def output_extension(self):
        return self._target_ext

    def convert(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        output_path = file_path + self._target_ext
        
        try:
            # 使用 ffmpeg 转换为高质量 GIF
            # 第一步：生成调色板以获得更好的颜色表现
            # 第二步：使用调色板进行转换
            # -vf: 滤镜
            # fps=10: 每秒10帧
            # scale=480:-1: 宽度480，高度按比例缩放
            # flags=lanczos: 缩放算法
            # split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse: 调色板生成与使用
            
            filter_complex = "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
            
            result = subprocess.run(
                ['ffmpeg', '-i', file_path, '-vf', filter_complex, '-y', output_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 读取转换后的 GIF 内容 (二进制)
            with open(output_path, 'rb') as f:
                content = f.read()
            
            # 清理生成的临时输出文件
            if os.path.exists(output_path):
                os.remove(output_path)
                
            return content, self._target_ext
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg GIF conversion failed: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error during GIF conversion: {str(e)}")
