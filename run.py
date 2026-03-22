import subprocess
import time
import socket
import webbrowser
import os
import sys
import shutil
import importlib.util

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

    # Check for pdf2docx (Python package)
    if importlib.util.find_spec("pdf2docx") is None:
        missing.append("pdf2docx")
        
    # Check for pillow-heif (Python package)
    if importlib.util.find_spec("pillow_heif") is None:
        missing.append("pillow-heif")
        
    # Check for realesrgan (Python package)
    if importlib.util.find_spec("realesrgan") is None:
        missing.append("realesrgan")
        
    return missing

def install_dependencies(missing_list):
    """Automatically installs missing Python dependencies."""
    python_deps = [dep for dep in missing_list if dep in ["pdf2docx", "pillow-heif", "realesrgan", "basicsr", "opencv-python"]]
    
    if not python_deps:
        return
        
    print(f"\n📦 检测到缺失 Python 依赖: {', '.join(python_deps)}")
    print("🚀 正在尝试自动安装...")
    
    try:
        # 使用当前 Python 环境进行 pip 安装
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + python_deps)
        print("✅ 依赖安装成功！\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ 自动安装失败: {e}. 请手动运行: pip install {' '.join(python_deps)}")
    except Exception as e:
        print(f"⚠️ 发生意外错误: {str(e)}")

def run():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(root_dir, "server")
    client_dir = os.path.join(root_dir, "client")

    print("==========================================")
    print("   All-to-All File Converter Launcher")
    print("==========================================")

    # 1. Start Backend
    def start_backend(server_dir):
        """Starts the Flask backend server."""
        print("🚀 正在启动后端服务 (app.py)...")
        
        # Pass missing dependencies as env var if any
        env = os.environ.copy()
        missing = check_dependencies()
        
        # 尝试自动安装缺失的 Python 依赖
        install_dependencies(missing)
        
        # 再次检查环境（安装后）
        missing = check_dependencies()
        
        if missing:
            env["MISSING_DEPS"] = "|".join(missing)
            print(f"⚠️ 启动提示: 仍有部分组件不可用: {', '.join(missing)}")
        
        backend_proc = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=server_dir,
            env=env, # Pass the modified environment
            # stdout=subprocess.DEVNULL, # 可选：完全隐藏输出
            # stderr=subprocess.DEVNULL
        )
        return backend_proc

    backend_proc = start_backend(server_dir)

    # 2. Start Frontend
    print("Starting Frontend (Vite)...")
    # Windows 下直接运行 npm 可能需要 shell=True
    frontend_proc = subprocess.Popen(
        "npm run dev",
        cwd=client_dir,
        shell=True,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL
    )

    # 3. Wait for Frontend
    print("Waiting for services to be ready...")
    ready = False
    for _ in range(30): # 最多等待 30 秒
        if is_port_open(5173):
            ready = True
            break
        time.sleep(1)

    if ready:
        print("Opening browser...")
        webbrowser.open("http://localhost:5173")
        print("\nAll systems go! Keep this window open to maintain services.")
        print("Press Ctrl+C to stop both servers.")
        
        try:
            while True:
                time.sleep(1)
                if backend_proc.poll() is not None:
                    print("Backend stopped unexpectedly.")
                    break
                if frontend_proc.poll() is not None:
                    print("Frontend stopped unexpectedly.")
                    break
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        print("Timed out waiting for services.")

    # Cleanup
    backend_proc.terminate()
    frontend_proc.terminate()

if __name__ == "__main__":
    run()
