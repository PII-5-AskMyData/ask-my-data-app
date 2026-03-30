import signal
import requests
import webview
import sys
import os
import subprocess
import time

def start_streamlit():
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    env = os.environ.copy()
    
    # Roda o Streamlit em modo headless (sem abrir o browser nativo automaticamente)
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", "8501", "--server.headless", "true"],
        env=env,
        preexec_fn=os.setsid 
    )

    return process

def wait_for_streamlit(url="http://localhost:8501", timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url)
            return True
        except:
            time.sleep(0.5)
    return False

def stop_streamlit(process):
    if process and process.poll() is None:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=5)
        except:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)

if __name__ == '__main__':
    # Usar pywebview como empacotador desktop de um servidor web interno  
    streamlit_process = start_streamlit()

    if wait_for_streamlit():
        print("Iniciando janela WebView da aplicacao...")
        window = webview.create_window("Ask My Data", "http://localhost:8501")
        webview.start(gui="gtk")
    else:
        print("Falha ao iniciar Streamlit.")

    stop_streamlit(streamlit_process)
