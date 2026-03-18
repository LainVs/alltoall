import pandas as pd
import tempfile
import os
import json
from .base import BaseConverter

class JsonConverter(BaseConverter):
    def __init__(self, source_ext=".json", target_ext=".xlsx"):
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
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 尝试规范化
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                # 尝试规范化单层字典或嵌套字典 (简单处理)
                df = pd.json_normalize(data)
            
            if self.output_extension == ".xlsx":
                tmp_xlsx = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                tmp_path = tmp_xlsx.name
                tmp_xlsx.close()
                try:
                    df.to_excel(tmp_path, index=False)
                    with open(tmp_path, "rb") as f:
                        content = f.read()
                    return content, self.output_extension
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else: # .csv
                return df.to_csv(index=False, encoding="utf-8-sig"), self.output_extension
        except Exception as e:
            raise RuntimeError(f"JSON conversion to {self.output_extension} failed: {str(e)}")
