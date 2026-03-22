import subprocess
import os
import tempfile
import fitz  # PyMuPDF
from .base import BaseConverter

class PandocConverter(BaseConverter):
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
            # 调用 pandoc 命令行工具
            # -s: standalone
            # -o: output
            result = subprocess.run(
                ['pandoc', file_path, '--from=markdown-yaml_metadata_block', '-s', '-o', output_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 读取转换后的文件内容
            # 对于二进制格式（如 docx），读取 bytes；对于文本格式，读取 str
            mode = 'rb' if self._target_ext in ['.docx', '.pdf'] else 'r'
            encoding = None if 'b' in mode else 'utf-8'
            
            with open(output_path, mode, encoding=encoding) as f:
                content = f.read()
            
            # 清理生成的临时输出文件，因为 app.py 会处理最终的发送和清理
            if os.path.exists(output_path):
                os.remove(output_path)
                
            return content, self._target_ext
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Pandoc conversion failed: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error during pandoc conversion: {str(e)}")

class MdToPdfConverter(BaseConverter):
    """
    Chained converter: Markdown ➔ DOCX (Pandoc) ➔ PDF (PyMuPDF).
    Avoids heavy TeX dependencies.
    """
    @property
    def supported_extension(self):
        return ".md"

    @property
    def output_extension(self):
        return ".pdf"

    def convert(self, file_path):
        # 1. MD ➔ DOCX (using Pandoc)
        docx_converter = PandocConverter(".md", ".docx")
        docx_content, _ = docx_converter.convert(file_path)
        
        # 2. DOCX ➔ PDF (using Fitz/PyMuPDF)
        # Fitz can open docx and convert to PDF bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            tmp_docx.write(docx_content)
            tmp_docx_path = tmp_docx.name
        
        try:
            doc = fitz.open(tmp_docx_path)
            pdf_bytes = doc.convert_to_pdf()
            doc.close()
            return pdf_bytes, self.output_extension
        finally:
            if os.path.exists(tmp_docx_path):
                os.remove(tmp_docx_path)
