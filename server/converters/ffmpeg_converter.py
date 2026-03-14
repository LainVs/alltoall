import subprocess
import os
from .base import BaseConverter

class FFmpegConverter(BaseConverter):
    def __init__(self, source_ext, target_ext):
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
            # 使用 ffmpeg 提取音频
            # -i: input
            # -vn: disable video
            # -ab: audio bitrate (optional)
            # -y: overwrite output files
            result = subprocess.run(
                ['ffmpeg', '-i', file_path, '-vn', '-y', output_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 读取转换后的音频内容 (二进制)
            with open(output_path, 'rb') as f:
                content = f.read()
            
            # 清理生成的临时输出文件
            if os.path.exists(output_path):
                os.remove(output_path)
                
            return content, self._target_ext
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg conversion failed: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error during ffmpeg conversion: {str(e)}")
