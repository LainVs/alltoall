from abc import ABC, abstractmethod

class BaseConverter(ABC):
    @abstractmethod
    def convert(self, file_path):
        """
        处理文件转换的逻辑。
        :param file_path: 待转换文件的绝对路径
        :return: 转换后的文件内容 (str or bytes) 以及 建议的文件后缀
        """
        pass

    @property
    @abstractmethod
    def supported_extension(self):
        """
        返回此转换器支持的源文件后缀（如 '.ipynb'）
        """
        pass

    @property
    @abstractmethod
    def output_extension(self):
        """
        返回转换后的文件后缀（如 '.md'）
        """
        pass
