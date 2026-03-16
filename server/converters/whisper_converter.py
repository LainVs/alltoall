import os
import whisper
import docx
import fitz
from .base import BaseConverter

class WhisperConverter(BaseConverter):
    def __init__(self, source_ext, target_ext, model_size="base"):
        self._source_ext = source_ext
        self._target_ext = target_ext
        self._model_size = model_size
        self._model = None

    @property
    def supported_extension(self):
        return self._source_ext

    @property
    def output_extension(self):
        return self._target_ext

    def _get_model(self):
        if self._model is None:
            # 首次调用时加载模型
            print(f"Loading Whisper model: {self._model_size}...")
            self._model = whisper.load_model(self._model_size)
        return self._model

    def convert(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            model = self._get_model()
            
            # 执行识别
            # fp16=False 可以在没有 GPU 的机器上更稳定运行
            # initial_prompt 引导模型输出简体中文
            result = model.transcribe(
                file_path, 
                fp16=False, 
                language="zh",
                initial_prompt="以下是普通话的简体中文。"
            )
            text = result["text"].strip()
            
            # 根据目标后缀返回内容
            if self._target_ext == ".md":
                filename = os.path.basename(file_path)
                return f"# Transcription of {filename}\n\n{text}", self._target_ext
            
            elif self._target_ext == ".docx":
                doc = docx.Document()
                doc.add_heading(f"Transcription of {os.path.basename(file_path)}", 0)
                doc.add_paragraph(text)
                
                # 保存到流或内存中？BaseConverter 期望内容。
                # app.py 会将内容写入 BytesIO。
                # 所以我可以直接返回 bytes。
                import io
                doc_io = io.BytesIO()
                doc.save(doc_io)
                return doc_io.getvalue(), self._target_ext
                
            elif self._target_ext == ".pdf":
                # 使用 fitz 创建简单的 PDF
                doc = fitz.open()
                page = doc.new_page()
                
                # 定义中文字体路径 (Windows 常用字体)
                font_path = r"C:\Windows\Fonts\msyh.ttc"
                font_name = "msyh"
                
                # 如果字体不存在，尝试使用内置的或其他备选
                if os.path.exists(font_path):
                    page.insert_font(fontname=font_name, fontfile=font_path)
                else:
                    # 备选：如果是在 Linux 或其他系统，可能需要不同路径
                    font_name = "helv" # 回退到默认，但中文会乱码
                
                # 写入标题
                page.insert_text((50, 72), f"Transcription of {os.path.basename(file_path)}", 
                                 fontsize=16, fontname=font_name)
                
                # 写入正文 (使用 textbox 支持换行)
                rect = fitz.Rect(50, 100, 550, 800)
                page.insert_textbox(rect, text, fontname=font_name, fontsize=11)
                
                pdf_bytes = doc.convert_to_pdf()
                doc.close()
                return pdf_bytes, self._target_ext
            
            return text, self._target_ext
            
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")
