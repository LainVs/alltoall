import fitz  # PyMuPDF
import os
from PIL import Image
import pillow_heif
from .base import BaseConverter

class ImageToPdfConverter(BaseConverter):
    """
    Converter for image files (JPG, PNG, WebP, BMP) to PDF.
    """
    def __init__(self, source_ext=".jpg", target_ext=".pdf"):
        self._source_ext = source_ext
        self._target_ext = target_ext

    @property
    def supported_extension(self):
        return self._source_ext

    @property
    def output_extension(self):
        return self._target_ext

    def convert(self, file_path, **kwargs):
        # PyMuPDF can open various image formats and convert them to PDF
        img_doc = fitz.open(file_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_doc.close()
        return pdf_bytes, self.output_extension

class HeicToJpgConverter(BaseConverter):
    """
    Converter for HEIC images (iPhone) to JPG or PNG.
    """
    def __init__(self, source_ext=".heic", target_ext=".jpg"):
        self._source_ext = source_ext
        self._target_ext = target_ext
        # Register HEIF opener for Pillow
        pillow_heif.register_heif_opener()

    @property
    def supported_extension(self):
        return self._source_ext

    @property
    def output_extension(self):
        return self._target_ext

    def convert(self, file_path, **kwargs):
        # Open HEIC image using Pillow (enabled by pillow_heif)
        image = Image.open(file_path)
        
        # Binary content buffer
        import io
        img_byte_arr = io.BytesIO()
        
        # If target is JPEG and source has alpha channel, convert to RGB
        if self.output_extension.lower() in [".jpg", ".jpeg"] and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        format_name = "JPEG" if self.output_extension.lower() in [".jpg", ".jpeg"] else "PNG"
        image.save(img_byte_arr, format=format_name, quality=95)
        
        return img_byte_arr.getvalue(), self.output_extension

class ImageUpscaleConverter(BaseConverter):
    """
    AI Image Super-Resolution (Upscaling) using Real-ESRGAN.
    """
    def __init__(self, scale=4):
        self.scale = scale
        self.model = None
        self.upsampler = None

    @property
    def supported_extension(self):
        return ".jpg" # Base image types supported

    @property
    def output_extension(self):
        return f"_x{self.scale}.jpg"

    def _init_model(self, device_pref='auto'):
        if self.upsampler is not None:
            return

        try:
            import torch
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            
            # Determine device
            if device_pref == 'gpu' and torch.cuda.is_available():
                device = torch.device('cuda')
            elif device_pref == 'dml':
                import torch_directml
                device = torch_directml.device()
            elif torch.cuda.is_available():
                device = torch.device('cuda')
            else:
                device = torch.device('cpu')
                
            # Use RRDBNet for Real-ESRGAN (x4 model)
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            
            # This will download the model weights to the default location if not present
            self.upsampler = RealESRGANer(
                scale=4,
                model_path=None, # It will find/download the default 'RealESRGAN_x4plus.pth'
                model=model,
                tile=400, # Tile size to save memory
                tile_pad=10,
                pre_pad=0,
                half=True if device.type == 'cuda' else False, # fp16 for CUDA
                device=device
            )
        except ImportError:
            raise RuntimeError("请先安装 realesrgan 和 basicsr 库 (pip install realesrgan basicsr)")
        except Exception as e:
            raise RuntimeError(f"AI 模型初始化失败: {str(e)}")

    def convert(self, file_path, **kwargs):
        import cv2
        import numpy as np
        import io
        
        device_pref = kwargs.get('device_pref', 'auto')
        self._init_model(device_pref)
        
        # Read image with OpenCV
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("无法读取图片文件")
            
        # Run upscaling
        output, _ = self.upsampler.enhance(img, outscale=self.scale)
        
        # Encode back to bytes
        is_success, buffer = cv2.imencode(".jpg", output, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        if not is_success:
            raise RuntimeError("图片编码失败")
            
        return buffer.tobytes(), self.output_extension
