import os
import pandas as pd
import tempfile
import fitz  # PyMuPDF
import subprocess
from .base import BaseConverter



class PdfToWordConverter(BaseConverter):
    @property
    def supported_extension(self):
        return ".pdf"

    @property
    def output_extension(self):
        return ".docx"

    def convert(self, file_path):
        # 使用 pdf2docx 进行转换
        docx_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        docx_path = docx_file.name
        docx_file.close()
        
        try:
            from pdf2docx import Converter
            cv = Converter(file_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            
            with open(docx_path, "rb") as f:
                content = f.read()
            return content, self.output_extension
        finally:
            if os.path.exists(docx_path):
                os.remove(docx_path)

class ExcelConverter(BaseConverter):
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
        try:
            if self.supported_extension == ".xlsx" and self.output_extension == ".csv":
                df = pd.read_excel(file_path)
                # 返回 csv 内容字符串
                return df.to_csv(index=False, encoding='utf-8-sig'), self.output_extension
            elif self.supported_extension == ".csv" and self.output_extension == ".xlsx":
                # xlsx 是二进制格式，需要写入字节
                tmp_xlsx = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                tmp_path = tmp_xlsx.name
                tmp_xlsx.close() # 关闭句柄，防止 Windows 锁定
                
                try:
                    df = pd.read_csv(file_path)
                    df.to_excel(tmp_path, index=False)
                    with open(tmp_path, "rb") as f:
                        content = f.read()
                    return content, self.output_extension
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else:
                raise ValueError(f"Unsupported conversion: {self.supported_extension} to {self.output_extension}")
        except Exception as e:
            raise RuntimeError(f"Excel conversion failed: {str(e)}")

class DocxToPdfConverter(BaseConverter):
    @property
    def supported_extension(self):
        return ".docx"

    @property
    def output_extension(self):
        return ".pdf"

    def convert(self, file_path):
        try:
            # 使用 fitz (PyMuPDF) 进行转换
            doc = fitz.open(file_path)
            pdf_bytes = doc.convert_to_pdf()
            doc.close()
            return pdf_bytes, self.output_extension
        except Exception as e:
            raise RuntimeError(f"Docx to PDF conversion failed via fitz: {str(e)}")

