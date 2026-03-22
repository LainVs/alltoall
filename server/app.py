from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import tempfile
import io
from converters.ipynb_to_md import IpynbToMdConverter
from converters.pandoc_converter import PandocConverter, MdToPdfConverter
from converters.whisper_converter import WhisperConverter
from converters.office_converters import ExcelConverter, DocxToPdfConverter, PdfToWordConverter
from converters.video_to_gif import VideoToGifConverter
from converters.pdf_converters import PdfToImageConverter, PdfToTextConverter
from converters.data_converters import JsonConverter
from converters.ipynb_converters import IpynbToHtmlConverter
from converters.image_converters import ImageToPdfConverter, HeicToJpgConverter, ImageUpscaleConverter
from converters.ffmpeg_converter import FFmpegConverter, VideoToImageConverter

import logging

# 配置日志到文件
logging.basicConfig(
    filename='server.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 注册转换器
# 格式: { source_ext: { target_ext: converter_instance } }
# 使用 small 模型，在性能 and 准确度之间取得平衡 (中文识别大幅提升)
whisper_converter_md = WhisperConverter("", ".md", model_size="small")
whisper_converter_txt = WhisperConverter("", ".txt", model_size="small")
whisper_converter_docx = WhisperConverter("", ".docx", model_size="small")
whisper_converter_pdf = WhisperConverter("", ".pdf", model_size="small")

# 实例化图片转换器
img_to_pdf = ImageToPdfConverter()
heic_to_jpg = HeicToJpgConverter(target_ext=".jpg")
heic_to_png = HeicToJpgConverter(target_ext=".png")
img_upscale_x2 = ImageUpscaleConverter(scale=2)
img_upscale_x4 = ImageUpscaleConverter(scale=4)
pdf_to_word = PdfToWordConverter()

converters_map = {
    ".ipynb": {
        ".md": IpynbToMdConverter(),
        ".html": IpynbToHtmlConverter()
    },
    ".md": {
        ".docx": PandocConverter(".md", ".docx"),
        ".html": PandocConverter(".md", ".html"),
        ".pdf": MdToPdfConverter()
    },
    ".docx": {
        ".md": PandocConverter(".docx", ".md"),
        ".pdf": DocxToPdfConverter()
    },
    ".pdf": {
        ".png": PdfToImageConverter(target_ext=".png"),
        ".jpg": PdfToImageConverter(target_ext=".jpg"),
        ".txt": PdfToTextConverter(),
        ".docx": pdf_to_word
    },
    ".json": {
        ".xlsx": JsonConverter(target_ext=".xlsx"),
        ".csv": JsonConverter(target_ext=".csv")
    },
    ".xlsx": {
        ".csv": ExcelConverter(".xlsx", ".csv")
    },
    ".csv": {
        ".xlsx": ExcelConverter(".csv", ".xlsx")
    },
    ".html": {
        ".md": PandocConverter(".html", ".md")
    },
    ".mp4": {
        ".mp3": FFmpegConverter(".mp4", ".mp3"),
        ".wav": FFmpegConverter(".mp4", ".wav"),
        ".aac": FFmpegConverter(".mp4", ".aac"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt,
        ".docx": whisper_converter_docx,
        ".pdf": whisper_converter_pdf,
        ".gif": VideoToGifConverter(".mp4"),
        ".jpg": VideoToImageConverter(".mp4")
    },
    ".mp3": {
        ".wav": FFmpegConverter(".mp3", ".wav"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt,
        ".docx": whisper_converter_docx,
        ".pdf": whisper_converter_pdf
    },
    ".wav": {
        ".mp3": FFmpegConverter(".wav", ".mp3"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt,
        ".docx": whisper_converter_docx,
        ".pdf": whisper_converter_pdf
    },
    ".mkv": {
        ".mp3": FFmpegConverter(".mkv", ".mp3"),
        ".wav": FFmpegConverter(".mkv", ".wav"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt,
        ".docx": whisper_converter_docx,
        ".pdf": whisper_converter_pdf,
        ".gif": VideoToGifConverter(".mkv"),
        ".jpg": VideoToImageConverter(".mkv")
    },
    ".mov": {
        ".mp3": FFmpegConverter(".mov", ".mp3"),
        ".docx": whisper_converter_docx,
        ".pdf": whisper_converter_pdf,
        ".gif": VideoToGifConverter(".mov"),
        ".jpg": VideoToImageConverter(".mov")
    },
    ".avi": {
        ".mp3": FFmpegConverter(".avi", ".mp3"),
        ".gif": VideoToGifConverter(".avi"),
        ".jpg": VideoToImageConverter(".avi")
    },
    ".flv": {
        ".mp3": FFmpegConverter(".flv", ".mp3"),
        ".gif": VideoToGifConverter(".flv"),
        ".jpg": VideoToImageConverter(".flv")
    },
    ".wmv": {
        ".mp3": FFmpegConverter(".wmv", ".mp3"),
        ".gif": VideoToGifConverter(".wmv"),
        ".jpg": VideoToImageConverter(".wmv")
    },
    ".webm": {
        ".mp3": FFmpegConverter(".webm", ".mp3"),
        ".gif": VideoToGifConverter(".webm"),
        ".jpg": VideoToImageConverter(".webm")
    },
    ".jpg": {
        ".pdf": img_to_pdf,
        " AI 放大 x2": img_upscale_x2,
        " AI 放大 x4": img_upscale_x4
    },
    ".jpeg": {
        ".pdf": img_to_pdf,
        " AI 放大 x2": img_upscale_x2,
        " AI 放大 x4": img_upscale_x4
    },
    ".png": {
        ".pdf": img_to_pdf,
        " AI 放大 x2": img_upscale_x2,
        " AI 放大 x4": img_upscale_x4
    },
    ".webp": {
        ".pdf": img_to_pdf
    },
    ".bmp": {
        ".pdf": img_to_pdf,
        " AI 放大 x2": img_upscale_x2,
        " AI 放大 x4": img_upscale_x4
    },
    ".heic": {
        ".jpg": heic_to_jpg,
        ".png": heic_to_png,
        " AI 放大 x2": img_upscale_x2,
        " AI 放大 x4": img_upscale_x4
    }
}

@app.route('/formats', methods=['GET'])
def get_formats():
    """Returns the map of supported conversion formats and system status."""
    missing_deps = os.environ.get("MISSING_DEPS", "").split("|") if os.environ.get("MISSING_DEPS") else []
    
    return jsonify({
        "supported_formats": {ext: list(targets.keys()) for ext, targets in converters_map.items()},
        "system_status": {
            "ready": len(missing_deps) == 0,
            "missing_deps": missing_deps
        }
    })

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    target_format = request.form.get('target_format')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    src_ext = os.path.splitext(file.filename)[1].lower()
    
    if src_ext not in converters_map:
        return jsonify({"error": f"Unsupported source type: {src_ext}"}), 400
    
    available_targets = converters_map[src_ext]
    
    # 如果没指定目标格式且只有一个可用，则默认使用那个
    if not target_format:
        if len(available_targets) == 1:
            target_format = list(available_targets.keys())[0]
        else:
            return jsonify({"error": f"Target format required for {src_ext}. Available: {list(available_targets.keys())}"}), 400
            
    if target_format not in available_targets:
        return jsonify({"error": f"Unsupported target format: {target_format} for {src_ext}"}), 400
        
    converter = available_targets[target_format]
    
    # 使用临时文件处理
    temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=src_ext)
    try:
        file.save(temp_in.name)
        temp_in_path = temp_in.name
        temp_in.close()  # 必须先关闭，否则在 Windows 上 Pandoc 等外部工具无法读取
        
        kwargs = {}
        if isinstance(converter, WhisperConverter):
            kwargs['device_pref'] = request.form.get('device_pref', 'auto')
            
        content, out_ext = converter.convert(temp_in_path, **kwargs)
        
        # 处理输出文件名
        base_name = os.path.splitext(file.filename)[0]
        out_filename = base_name + out_ext
        
        # 准备响应内容
        if isinstance(content, str):
            content_io = io.BytesIO(content.encode('utf-8'))
        elif isinstance(content, bytes):
            content_io = io.BytesIO(content)
        else:
            # 如果 converter 直接返回了文件流
            content_io = content
            
        return send_file(
            content_io,
            as_attachment=True,
            download_name=out_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保输入临时文件被删除
        if 'temp_in_path' in locals() and os.path.exists(temp_in_path):
            try:
                os.remove(temp_in_path)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
