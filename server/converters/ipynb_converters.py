import nbformat
from nbconvert import HTMLExporter
from .base import BaseConverter

class IpynbToHtmlConverter(BaseConverter):
    def __init__(self, source_ext=".ipynb", target_ext=".html"):
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
                nb = nbformat.read(f, as_version=4)
            
            html_exporter = HTMLExporter()
            (body, resources) = html_exporter.from_notebook_node(nb)
            return body, self.output_extension
        except Exception as e:
            raise RuntimeError(f"Notebook to HTML conversion failed: {str(e)}")
