import nbformat
from nbconvert import MarkdownExporter
from .base import BaseConverter
import os

class IpynbToMdConverter(BaseConverter):
    @property
    def supported_extension(self):
        return ".ipynb"

    @property
    def output_extension(self):
        return ".md"

    def convert(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            nb_content = nbformat.read(f, as_version=4)

        md_exporter = MarkdownExporter()
        (body, resources) = md_exporter.from_notebook_node(nb_content)
        
        return body, self.output_extension
