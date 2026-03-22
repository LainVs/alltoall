# AllToAll 功能指南

AllToAll 是一款极简、专业且完全本地化的文件转换工具。

## 核心功能

- **多文件批处理**: 支持同时拖入多个文件进行一键批量转换。
- **直观拖拽界面**: 极简设计，支持直接拖拽文件或包含多层嵌套的整个文件夹上传。
- **智能格式推荐**: 根据输入文件自动列出最合适的转换目标。
- **本地 AI 驱动**: 集成 OpenAI Whisper 本地模型，提供高精度的语音转文字服务。
- **多媒体处理**:
  - **视频提音**: 从视频 (.mp4, .mkv, .mov, .avi, .flv, .wmv, .webm) 中快速提取音频 (.mp3, .wav, .aac)。
  - **媒体转文档**: 将视频或音频直接转录为 Word (.docx)、PDF (.pdf)、Markdown (.md) 或文本 (.txt)。
  - **GIF 制作**: 支持将视频 (.mp4, .mkv, .mov, .avi, .flv, .wmv, .webm) 转换为高质量的 GIF 动图。
  - **封面提取**: 从视频文件中自动提取第一帧作为 JPEG 封面图。
- **办公与数据增强**: 
  - **图片转换**: 支持图片 (.jpg, .png, .webp, .bmp) ➔ PDF (.pdf) 以及 PDF 转图片 (.png, .jpg)。
- **PDF 处理**: PDF ➔ Word (.docx), 图片 (.png, .jpg), 提取文本 (.txt)。
  - **Word 转 PDF**: 高质量 Word (.docx) ➔ PDF 转换。
  - **表格互转**: Excel (.xlsx) ↔ CSV 完美互转。
  - **数据导出**: 支持 JSON ➔ Excel (.xlsx) 或 CSV。
  - **Notebook 转换**: Jupyter Notebook (.ipynb) ➔ HTML 或 Markdown (.md)。
- **高性能与可靠性**: 优化了启动过程中的格式加载逻辑，支持自动重试，确保转换选项在任何时候都能准确显示。
- **智能硬件加速**: 高级设置中支持自由切换 CPU/GPU 加速模式，并具备在显卡不兼容时自动无缝退回 CPU 的安全报错保护机制。

## 支持的转换格式

### 文档、表格与数据
- **Markdown (.md)** ↔ Word (.docx), HTML, PDF
- **Word (.docx)** ➔ PDF, Markdown (.md)
- **Excel (.xlsx)** ↔ CSV
- **图片 (.jpg, .png, .webp, .bmp)** ➔ PDF
- **PDF** ➔ Word (.docx), PNG, JPG, Text (.txt)
- **JSON** ➔ Excel (.xlsx), CSV
- **Jupyter Notebook (.ipynb)** ➔ HTML, Markdown (.md)

### 媒体类
- **视频提取**: MP4 / MKV / MOV / AVI / FLV / WMV / WEBM ➔ MP3, WAV, AAC, JPG (封面)
- **GIF 制作**: MP4 / MKV / MOV / AVI / FLV / WMV / WEBM ➔ GIF
- **内容转录**: MP4 / MP3 / WAV / MKV / MOV ➔ Word (.docx), PDF (.pdf), Markdown (.md), Text (.txt)

## 操作步骤
1. **启动**: 运行 `start.bat` 文件，稍等片刻将自动打开浏览器界面。
2. **上传**: 拖入想要转换的一个或多个文件。
3. **选择**: 搜索并点击你想要的目标格式。
4. **转换**: 点击“转换为...”按钮，转换完成后文件将自动下载。

---
*喵*
