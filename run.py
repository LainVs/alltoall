import subprocess
import time
import socket
import webbrowser
import os
import sys
import shutil
import importlib.util

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_core_dependencies():
    """检查核心必备依赖（缺少则无法运行）"""
    missing = []
    
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg (用于视频和音频转换)")
        
    if not shutil.which("pandoc"):
        missing.append("pandoc (用于文档格式转换)")
    
    return missing

def check_optional_dependencies():
    """检查可选依赖（缺少只影响部分功能）"""
    optional_missing = []
    optional_available = []
    
    if importlib.util.find_spec("pillow_heif") is not None:
        optional_available.append("HEIC 图片转换")
    else:
        optional_missing.append("pillow-heif (HEIC 图片转换)")
        
    if importlib.util.find_spec("realesrgan") is not None and importlib.util.find_spec("basicsr") is not None:
        optional_available.append("AI 图片超分")
    else:
        optional_missing.append("realesrgan + basicsr (AI 图片超分)")

    if importlib.util.find_spec("pdf2docx") is not None:
        optional_available.append("PDF 转 Word")
    else:
        optional_missing.append("pdf2docx (PDF 转 Word)")
        
    return optional_missing, optional_available

def run():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(root_dir, "server")
    client_dir = os.path.join(root_dir, "client")

    print("==========================================")
    print("   All-to-All 文件转换器 启动中...")
    print("==========================================")

    # 1. 检查核心依赖
    core_missing = check_core_dependencies()
    if core_missing:
        print("")
        print("[警告] 以下核心工具未安装（部分转换功能将不可用）:")
        for dep in core_missing:
            print(f"   - {dep}")
        print("")
    
    # 2. 检查可选依赖（只提示，不阻塞）
    opt_missing, opt_available = check_optional_dependencies()
    if opt_available:
        print(f"[已就绪] 可选功能: {', '.join(opt_available)}")
    if opt_missing:
        print("[提示] 以下可选功能未安装（不影响核心使用）:")
        for dep in opt_missing:
            print(f"   - {dep}")
        print(f"   如需安装，请运行: pip install -r server/requirements-optional.txt")
    print("")

    # 3. 启动后端
    def start_backend(server_dir):
        """启动 Flask 后端服务"""
        print("[1/2] 正在启动后端服务...")
        
        env = os.environ.copy()
        if core_missing:
            env["MISSING_DEPS"] = "|".join(core_missing)
        
        backend_proc = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=server_dir,
            env=env,
        )
        return backend_proc

    backend_proc = start_backend(server_dir)

    # 4. 启动前端
    print("[2/2] 正在启动前端服务 (Vite)...")
    frontend_proc = subprocess.Popen(
        "npm run dev",
        cwd=client_dir,
        shell=True,
    )

    # 5. 等待前端就绪
    print("正在等待服务就绪...")
    print("")
    ready = False
    for _ in range(30):
        if is_port_open(5173):
            ready = True
            break
        time.sleep(1)

    if ready:
        print("正在打开浏览器...")
        webbrowser.open("http://localhost:5173")
        print("")
        print("==========================================")
        print("  所有服务已启动！")
        print("  保持此窗口打开以维持服务运行")
        print("  按 Ctrl+C 停止所有服务")
        print("==========================================")
        print("")
        
        try:
            while True:
                time.sleep(1)
                if backend_proc.poll() is not None:
                    print("[警告] 后端服务意外停止。")
                    break
                if frontend_proc.poll() is not None:
                    print("[警告] 前端服务意外停止。")
                    break
        except KeyboardInterrupt:
            print("")
            print("正在关闭服务...")
    else:
        print("[错误] 服务启动超时，请检查错误信息。")

    # 清理
    backend_proc.terminate()
    frontend_proc.terminate()

if __name__ == "__main__":
    run()
