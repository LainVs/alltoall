import os
import whisper
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
            # 如果是 .md，可以加一点格式，比如一个标题
            if self._target_ext == ".md":
                filename = os.path.basename(file_path)
                return f"# Transcription of {filename}\n\n{text}", self._target_ext
            
            return text, self._target_ext
            
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")
