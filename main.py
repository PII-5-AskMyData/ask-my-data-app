import webview
import threading
import sys
import os
import subprocess
import time
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_streamlit():
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    env = os.environ.copy()
    
    # Roda o Streamlit em modo headless (sem abrir o browser nativo automaticamente)
    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", "8501", "--server.headless", "true"],
        env=env
    )

if __name__ == '__main__':
    # Usar pywebview como empacotador desktop de um servidor web interno
    port = 8501
    
    if not is_port_in_use(port):
        t = threading.Thread(target=start_streamlit, daemon=True)
        t.start()
    
    # Aguarda o streamlit subir a porta
    retries = 30
    while not is_port_in_use(port) and retries > 0:
        time.sleep(1)
        retries -= 1
        
    if retries == 0:
        print("Aviso: Streamlit pode nao ter iniciado completamente a tempo.")
        
    print("Iniciando janela WebView da aplicacao...")
    webview.create_window(
        title='Ask My Data - Klabin [RAG]', 
        url=f'http://127.0.0.1:{port}', 
        width=1280, 
        height=800,
        confirm_close=True
    )
    # Executa a aplicacao desktop
    webview.start()
