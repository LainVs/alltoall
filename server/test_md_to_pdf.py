"""
测试新的 Markdown → PDF 转换器（Playwright + KaTeX 方案）
"""
import os
import sys

# 创建一个包含公式、表格、代码块的测试 Markdown 文件
TEST_MD = r"""# 数学公式渲染测试

## 行内公式

爱因斯坦的质能方程 $E = mc^2$ 是物理学中最著名的公式之一。

欧拉公式 $e^{i\pi} + 1 = 0$ 将五个最重要的数学常数联系在一起。

## 块级公式

薛定谔方程：

$$i\hbar\frac{\partial}{\partial t}\Psi(\mathbf{r},t) = \hat{H}\Psi(\mathbf{r},t)$$

麦克斯韦方程组：

$$\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}$$

$$\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\varepsilon_0\frac{\partial \mathbf{E}}{\partial t}$$

## 表格

| 特性 | 旧方案 (PyMuPDF) | 新方案 (Playwright) |
|------|------------------|---------------------|
| 公式渲染 | ❌ 不支持 | ✅ 完美 |
| 中文支持 | ⚠️ 经常方块 | ✅ 完美 |
| 排版质量 | ⭐ 很差 | ⭐⭐⭐⭐⭐ 优秀 |

## 代码块

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 计算前10个斐波那契数
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

## 列表

1. 第一项
2. 第二项
   - 子项 A
   - 子项 B
3. 第三项

> **注意**: 这是一个引用块，测试引用块样式。

---

*测试完成！如果这些内容都正确渲染了，说明新方案工作正常。*
"""

# 写入测试文件
test_md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_formula.md")
test_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_formula_output.pdf")

with open(test_md_path, "w", encoding="utf-8") as f:
    f.write(TEST_MD)

try:
    from converters.pandoc_converter import MdToPdfConverter
    
    converter = MdToPdfConverter()
    print(f"使用 Playwright: {converter._use_playwright}")
    print("开始转换...")
    
    pdf_bytes, ext = converter.convert(test_md_path)
    
    with open(test_pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    file_size = os.path.getsize(test_pdf_path)
    print(f"✅ 转换成功！")
    print(f"   输出文件: {test_pdf_path}")
    print(f"   文件大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"   文件格式: {ext}")
    
except Exception as e:
    print(f"❌ 转换失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    # 清理测试 Markdown 源文件（保留 PDF 输出用于查看）
    if os.path.exists(test_md_path):
        os.remove(test_md_path)
    print(f"\n测试 PDF 已保留在: {test_pdf_path}")
    print("请打开查看渲染效果。")
