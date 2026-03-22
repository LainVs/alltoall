import fitz  # PyMuPDF
import os
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
