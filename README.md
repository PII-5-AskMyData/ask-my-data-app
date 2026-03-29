# Ask My Data

TODO: Descrição do projeto

**Estrutura de pastas:**
```Plaintext
ask-my-data-app/
│
├── data/                   # Onde vai ficar o CSV com o dicionário SAP
├── chroma_db/              # Onde o banco vetorial vai salvar os dados localmente
├── src/                    # Onde colocaremos a lógica do RAG 
│
├── app.py                  # A interface em Streamlit
├── main.py                 # O arquivo que cria a janela Desktop (PyWebView)
├── requirements.txt        # Lista de bibliotecas
└── .gitignore              

```

## Como contribuir

### Baixando o Ollama:
- Baixe o Ollama para o seu sistema operacional [aqui](https://ollama.com/download).

### Baixando e rodando o modelo (Qwen2.5):
- Abra o terminal do seu computador (Prompt de Comando, PowerShell ou terminal do Linux/Mac).
- Digite o seguinte comando e dê enter: 
```Bash
ollama run qwen2.5-coder:1.5b
```
Na primeira vez, o Ollama vai fazer o download do arquivo do modelo (a versão de 1.5b pesa pouco mais de 1 GB). Assim que o download terminar, o seu terminal vai se transformar em um chat e você já poderá conversar com a IA. Digite `\bye` para sair.

### Clone o repositório:
- Clone o repositório para o seu local de preferência com o comando:
```Bash
git clone https://github.com/PII-5-AskMyData/ask-my-data-app
```
### Configurando o ambiente python:
- Dentro do projeto rode os seguintes comandos pelo seu terminal:

**No Windows:**
```Bash
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

**No Mac/Linux:**
```Bash
python3 -m venv venv
source venv\Scripts\activate
pip install -r requirements.txt
```

TODO: futuras instruções e adições sobre o projeto
