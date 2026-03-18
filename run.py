import subprocess
import time
import socket
import webbrowser
import os
import sys

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(root_dir, "server")
    client_dir = os.path.join(root_dir, "client")

    print("==========================================")
    print("   All-to-All File Converter Launcher")
    print("==========================================")

    # 1. Start Backend
    print("Starting Backend (Flask)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=server_dir,
        # stdout=subprocess.DEVNULL, # 可选：完全隐藏输出
        # stderr=subprocess.DEVNULL
    )

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
