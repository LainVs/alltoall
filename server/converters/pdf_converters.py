import fitz  # PyMuPDF
import os
import io
from .base import BaseConverter

class PdfToImageConverter(BaseConverter):
    def __init__(self, source_ext=".pdf", target_ext=".png"):
        self._source_ext = source_ext
        self._target_ext = target_ext

    @property
    def supported_extension(self):
        return self._source_ext

    @property
    def output_extension(self):
        return self._target_ext

    def convert(self, file_path):
        doc = fitz.open(file_path)
        # 默认只转换第一页作为预览/图片，或者可以根据需求合并/打成 zip
        # 这里为了演示，我们只取第一页
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x 缩放以获得更高清晰度
        img_bytes = pix.tobytes("png")
        doc.close()
        return img_bytes, self.output_extension

class PdfToTextConverter(BaseConverter):
    def __init__(self, source_ext=".pdf", target_ext=".txt"):
        self._source_ext = source_ext
        self._target_ext = target_ext

    @property
    def supported_extension(self):
        return self._source_ext

    @property
    def output_extension(self):
        return self._target_ext

    def convert(self, file_path):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text, self.output_extension
