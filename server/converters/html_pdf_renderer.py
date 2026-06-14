"""
html_pdf_renderer.py
====================
高质量 Markdown → PDF 转换模块。

技术方案：
  1. markdown-it-py 将 Markdown 解析为 HTML（支持表格、删除线、数学公式、代码块）
  2. 包裹成完整 HTML 页面，引入 KaTeX CDN 实现公式渲染
  3. Playwright (Chromium) 将 HTML 页面打印为 A4 PDF

同时导出辅助函数 create_pdf_from_html，可供 WhisperConverter 等模块复用。
"""

import os
import tempfile
from .base import BaseConverter

# ---------------------------------------------------------------------------
# KaTeX CDN 基地址
# ---------------------------------------------------------------------------
_KATEX_CDN = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"

# ---------------------------------------------------------------------------
# HTML 页面模板
# ---------------------------------------------------------------------------
_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>

<!-- KaTeX CSS -->
<link rel="stylesheet"
      href="{katex_cdn}/katex.min.css"
      crossorigin="anonymous">

<style>
/* ===== 基础排版（GitHub Markdown 风格） ===== */
:root {{
    --color-text:       #24292f;
    --color-heading:    #1a1a2e;
    --color-link:       #0969da;
    --color-border:     #d0d7de;
    --color-bg-code:    #f6f8fa;
    --color-bg-quote:   #f6f8fa;
    --color-bg-stripe:  #f6f8fa;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC',
                 -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica,
                 Arial, sans-serif;
    font-size: 14px;
    line-height: 1.8;
    color: var(--color-text);
    /* 页面内容区内边距，PDF 边距由 Playwright page.pdf() 控制 */
    padding: 0;
}}

/* ===== 标题 ===== */
h1, h2, h3, h4, h5, h6 {{
    color: var(--color-heading);
    margin-top: 1.4em;
    margin-bottom: 0.6em;
    font-weight: 600;
    line-height: 1.4;
}}
h1 {{ font-size: 2em;   border-bottom: 2px solid var(--color-border); padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid var(--color-border); padding-bottom: 0.25em; }}
h3 {{ font-size: 1.25em; }}
h4 {{ font-size: 1em; }}
h5 {{ font-size: 0.875em; }}
h6 {{ font-size: 0.85em; color: #57606a; }}

/* ===== 段落与正文 ===== */
p {{ margin: 0.8em 0; }}
a {{ color: var(--color-link); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
strong {{ font-weight: 600; }}
del {{ color: #6e7781; }}

/* ===== 列表 ===== */
ul, ol {{ padding-left: 2em; margin: 0.6em 0; }}
li {{ margin: 0.25em 0; }}
li > ul, li > ol {{ margin: 0.1em 0; }}

/* ===== 引用块 ===== */
blockquote {{
    margin: 1em 0;
    padding: 0.6em 1em;
    border-left: 4px solid #0969da;
    background: var(--color-bg-quote);
    color: #57606a;
}}
blockquote p {{ margin: 0.3em 0; }}

/* ===== 行内代码 ===== */
code {{
    font-family: 'Cascadia Code', 'Fira Code', 'Source Code Pro',
                 Consolas, 'Courier New', monospace;
    font-size: 0.9em;
    background: var(--color-bg-code);
    padding: 0.15em 0.4em;
    border-radius: 4px;
    border: 1px solid var(--color-border);
}}

/* ===== 围栏代码块 ===== */
pre {{
    margin: 1em 0;
    padding: 1em;
    background: var(--color-bg-code);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    overflow-x: auto;
    line-height: 1.5;
}}
pre code {{
    background: none;
    padding: 0;
    border: none;
    border-radius: 0;
    font-size: 0.85em;
}}

/* ===== 表格 ===== */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 0.9em;
}}
th, td {{
    border: 1px solid var(--color-border);
    padding: 8px 12px;
    text-align: left;
}}
th {{
    background: var(--color-bg-code);
    font-weight: 600;
}}
/* 斑马条纹 */
tbody tr:nth-child(even) {{
    background: var(--color-bg-stripe);
}}

/* ===== 水平线 ===== */
hr {{
    border: none;
    border-top: 2px solid var(--color-border);
    margin: 2em 0;
}}

/* ===== 图片 ===== */
img {{
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 0.5em 0;
}}

/* ===== KaTeX 公式微调 ===== */
.katex-display {{
    margin: 1em 0;
    overflow-x: auto;
    overflow-y: hidden;
}}

/* ===== 打印优化 ===== */
@media print {{
    body {{ font-size: 12pt; }}
    pre, blockquote {{ page-break-inside: avoid; }}
    h1, h2, h3 {{ page-break-after: avoid; }}
    table {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>

{body}

<!-- KaTeX JS -->
<script src="{katex_cdn}/katex.min.js" crossorigin="anonymous"></script>
<script src="{katex_cdn}/contrib/auto-render.min.js" crossorigin="anonymous"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {{
    renderMathInElement(document.body, {{
        delimiters: [
            {{ left: "$$",  right: "$$",  display: true  }},
            {{ left: "$",   right: "$",   display: false }},
            {{ left: "\\\\(", right: "\\\\)", display: false }},
            {{ left: "\\\\[", right: "\\\\]", display: true  }}
        ],
        throwOnError: false
    }});
}});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Markdown → HTML 转换
# ---------------------------------------------------------------------------
def _markdown_to_html(md_text: str) -> str:
    """
    使用 markdown-it-py 将 Markdown 文本转换为 HTML 片段。

    启用扩展：table、strikethrough、dollarmath（行内 $ 和块级 $$）。
    """
    from markdown_it import MarkdownIt
    from mdit_py_plugins.dollarmath import dollarmath_plugin

    md = (
        MarkdownIt("commonmark", {"html": True})
        .enable("table")
        .enable("strikethrough")
    )
    # 注册 $...$ 和 $$...$$ 数学公式插件
    dollarmath_plugin(md, double_inline=True)

    return md.render(md_text)


# ---------------------------------------------------------------------------
# 构建完整 HTML 页面
# ---------------------------------------------------------------------------
def _build_full_html(body_html: str, title: str = "") -> str:
    """
    将 HTML 片段包裹成完整的 HTML 页面（含 KaTeX 引用和 CSS 样式）。
    """
    return _HTML_TEMPLATE.format(
        title=title or "Document",
        katex_cdn=_KATEX_CDN,
        body=body_html,
    )


# ---------------------------------------------------------------------------
# Playwright HTML → PDF
# ---------------------------------------------------------------------------
def _html_to_pdf(full_html: str) -> bytes:
    """
    使用 Playwright（sync API）将完整 HTML 页面渲染为 A4 PDF。

    流程：
      1. 将 HTML 写入临时 .html 文件
      2. 启动 headless Chromium 并加载该文件
      3. 等待 networkidle（确保 KaTeX CDN 资源加载完毕）
      4. 额外等待 500ms 确保公式渲染完成
      5. 调用 page.pdf() 输出 A4 尺寸 PDF
    """
    tmp_html_path = None
    try:
        # 写入临时 HTML 文件
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".html",
            encoding="utf-8",
            delete=False,
        ) as tmp:
            tmp.write(full_html)
            tmp_html_path = tmp.name

        # 启动 Playwright Chromium
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError(
                "未安装 playwright，请运行：pip install playwright && python -m playwright install chromium"
            )

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                raise RuntimeError(
                    f"无法启动 Chromium 浏览器，请确保已运行：python -m playwright install chromium\n"
                    f"错误详情：{e}"
                )

            page = browser.new_page()

            # 使用 file:/// 协议加载本地 HTML
            file_url = "file:///" + tmp_html_path.replace("\\", "/")
            page.goto(file_url, wait_until="networkidle")

            # 额外等待，确保 KaTeX 渲染完成
            page.wait_for_timeout(500)

            # 生成 A4 PDF
            pdf_bytes = page.pdf(
                format="A4",
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm",
                },
                print_background=True,
            )

            browser.close()

        return pdf_bytes

    finally:
        # 清理临时文件
        if tmp_html_path and os.path.exists(tmp_html_path):
            try:
                os.remove(tmp_html_path)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# 公共辅助函数（供外部模块复用）
# ---------------------------------------------------------------------------
def create_pdf_from_html(html_body: str, title: str = "") -> bytes:
    """
    将 HTML 片段包裹成完整页面并转换为 PDF。

    这是一个便捷函数，可被其他转换器（如 WhisperConverter）复用，
    用于将格式化好的 HTML 内容生成高质量 PDF。

    :param html_body: HTML 片段（<body> 内的内容）
    :param title:     页面标题（可选）
    :return:          PDF 文件的二进制内容 (bytes)
    """
    full_html = _build_full_html(html_body, title=title)
    return _html_to_pdf(full_html)


# ---------------------------------------------------------------------------
# MdToHtmlPdfConverter —— 继承 BaseConverter
# ---------------------------------------------------------------------------
class MdToHtmlPdfConverter(BaseConverter):
    """
    高质量 Markdown → PDF 转换器。

    使用 markdown-it-py 解析 Markdown（支持表格、删除线、数学公式），
    通过 KaTeX CDN 渲染公式，最终由 Playwright Chromium 生成 A4 PDF。
    """

    @property
    def supported_extension(self):
        return ".md"

    @property
    def output_extension(self):
        return ".pdf"

    def convert(self, file_path):
        """
        将 Markdown 文件转换为高质量 PDF。

        :param file_path: Markdown 文件的绝对路径
        :return: (pdf_bytes, '.pdf')
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件未找到：{file_path}")

        # 1. 读取 Markdown 源文件
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        # 2. Markdown → HTML 片段
        html_body = _markdown_to_html(md_text)

        # 3. 获取文件名作为页面标题
        title = os.path.splitext(os.path.basename(file_path))[0]

        # 4. 包裹完整 HTML 页面 → PDF
        pdf_bytes = create_pdf_from_html(html_body, title=title)

        return pdf_bytes, self.output_extension
