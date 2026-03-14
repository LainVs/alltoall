from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import tempfile
import io
from converters.ipynb_to_md import IpynbToMdConverter
from converters.pandoc_converter import PandocConverter
from converters.ffmpeg_converter import FFmpegConverter
from converters.whisper_converter import WhisperConverter

app = Flask(__name__)
CORS(app)

# 注册转换器
# 格式: { source_ext: { target_ext: converter_instance } }
# 使用 small 模型，在性能和准确度之间取得平衡 (中文识别大幅提升)
whisper_converter_md = WhisperConverter("", ".md", model_size="small")
whisper_converter_txt = WhisperConverter("", ".txt", model_size="small")

converters_map = {
    ".ipynb": {
        ".md": IpynbToMdConverter()
    },
    ".md": {
        ".docx": PandocConverter(".md", ".docx"),
        ".pdf": PandocConverter(".md", ".pdf"),
        ".html": PandocConverter(".md", ".html")
    },
    ".docx": {
        ".md": PandocConverter(".docx", ".md")
    },
    ".html": {
        ".md": PandocConverter(".html", ".md")
    },
    ".mp4": {
        ".mp3": FFmpegConverter(".mp4", ".mp3"),
        ".wav": FFmpegConverter(".mp4", ".wav"),
        ".aac": FFmpegConverter(".mp4", ".aac"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt
    },
    ".mp3": {
        ".wav": FFmpegConverter(".mp3", ".wav"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt
    },
    ".wav": {
        ".mp3": FFmpegConverter(".wav", ".mp3"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt
    },
    ".mkv": {
        ".mp3": FFmpegConverter(".mkv", ".mp3"),
        ".wav": FFmpegConverter(".mkv", ".wav"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt
    },
    ".mov": {
        ".mp3": FFmpegConverter(".mov", ".mp3"),
        ".md": whisper_converter_md,
        ".txt": whisper_converter_txt
    }
}

@app.route('/formats', methods=['GET'])
def get_formats():
    """返回支持的转换格式映射"""
    formats = {}
    for src, targets in converters_map.items():
        formats[src] = list(targets.keys())
    return jsonify(formats)

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
    with tempfile.NamedTemporaryFile(delete=False, suffix=src_ext) as temp_in:
        file.save(temp_in.name)
        temp_in_path = temp_in.name

    try:
        content, out_ext = converter.convert(temp_in_path)
        
        # 处理输出文件名
        keep_original_name = request.form.get('keep_name', 'true').lower() == 'true'
        base_name = os.path.splitext(file.filename)[0]
        out_filename = base_name + out_ext
        
        # 将内容写入二进制流以便发送（有些是 bytes，有些是 str）
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
            
        return send_file(
            io.BytesIO(content_bytes),
            as_attachment=True,
            download_name=out_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_in_path):
            os.remove(temp_in_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
