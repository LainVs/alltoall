import os
import tempfile
import fitz
from converters.pandoc_converter import MdToPdfConverter

# Create a sample markdown file
with open("test.md", "w", encoding="utf-8") as f:
    f.write("# Test Markdown\n\nThis is a *test* for MD to PDF conversion.\n\n- Item 1\n- Item 2")

try:
    conv = MdToPdfConverter()
    pdf_bytes, ext = conv.convert("test.md")
    
    with open("test_out.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    print(f"Success! Generated {os.path.getsize('test_out.pdf')} bytes.")
except Exception as e:
    print(f"Failed: {str(e)}")
finally:
    if os.path.exists("test.md"): os.remove("test.md")
    if os.path.exists("test_out.pdf"): os.remove("test_out.pdf")
