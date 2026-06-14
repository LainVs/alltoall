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

class _LegacyMdToPdfConverter(BaseConverter):
    """
    旧版链式转换器: Markdown → DOCX (Pandoc) → PDF (PyMuPDF)。
    作为备用方案保留，当 Playwright 不可用时使用。
    """
    @property
    def supported_extension(self):
        return ".md"

    @property
    def output_extension(self):
        return ".pdf"

    def convert(self, file_path):
        # 1. MD → DOCX (using Pandoc)
        docx_converter = PandocConverter(".md", ".docx")
        docx_content, _ = docx_converter.convert(file_path)
        
        # 2. DOCX → PDF (using Fitz/PyMuPDF)
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


class MdToPdfConverter(BaseConverter):
    """
    智能 Markdown → PDF 转换器。
    优先使用 Playwright + KaTeX 方案（高质量公式渲染），
    如果 Playwright 不可用则自动降级到旧的 Pandoc + PyMuPDF 方案。
    """
    def __init__(self):
        self._use_playwright = True
        # 启动时检测 Playwright 是否可用
        try:
            from .html_pdf_renderer import MdToHtmlPdfConverter
            self._modern_converter = MdToHtmlPdfConverter()
        except ImportError:
            print("提示: html_pdf_renderer 依赖未满足，MD→PDF 将使用旧版方案")
            self._use_playwright = False
            self._modern_converter = None
        
        self._legacy_converter = _LegacyMdToPdfConverter()

    @property
    def supported_extension(self):
        return ".md"

    @property
    def output_extension(self):
        return ".pdf"

    def convert(self, file_path):
        if self._use_playwright and self._modern_converter:
            try:
                return self._modern_converter.convert(file_path)
            except RuntimeError as e:
                # Playwright/Chromium 运行时不可用，降级到旧方案
                print(f"Playwright PDF 渲染失败，降级到旧版方案: {e}")
                return self._legacy_converter.convert(file_path)
        
        return self._legacy_converter.convert(file_path)

