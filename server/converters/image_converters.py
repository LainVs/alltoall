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
