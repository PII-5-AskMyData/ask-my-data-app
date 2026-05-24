# Ask My Data

Aplicação Streamlit para consultas em linguagem natural sobre dados SAP, com geração automática de SQL, gráficos e histórico por usuário.

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

## Persistência MongoDB

O projeto usa MongoDB para autenticação e armazenamento do fluxo do usuário:

- `users`: login e senha
- `conversation_history`: consultas, SQL gerado, explicação e gráfico estimado
- `saved_queries`: queries salvas por usuário

As variáveis principais ficam no `.env`:

- `MONGO_URI`
- `MONGO_DB_NAME`
- `MONGO_USERS_COLLECTION`
- `MONGO_CONVERSATIONS_COLLECTION`
- `MONGO_SAVED_QUERIES_COLLECTION`

## Pré-requisitos

Antes de rodar o projeto, garanta que você tenha instalado:

- Python 3.10 ou superior
- Ollama com o modelo `qwen2.5-coder:3b`
- MongoDB Atlas ou MongoDB local
- Um arquivo `.env` na raiz do projeto

## Exemplo de `.env`

Use este modelo como base para o seu arquivo local:

```Bash
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority
MONGO_DB_NAME=ask_my_data
MONGO_USERS_COLLECTION=users
MONGO_CONVERSATIONS_COLLECTION=conversation_history
MONGO_SAVED_QUERIES_COLLECTION=saved_queries
```

## Como contribuir

### Baixando o Ollama:

- Baixe o Ollama para o seu sistema operacional [aqui](https://ollama.com/download).

### Baixando e rodando o modelo (Qwen2.5):

- Abra o terminal do seu computador (Prompt de Comando, PowerShell ou terminal do Linux/Mac).
- Digite o seguinte comando e dê enter:

```Bash
ollama run qwen2.5-coder:3b
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
source venv/bin/activate
pip install -r requirements.txt
```

## Como rodar o projeto

Depois de configurar o ambiente e o `.env`, você pode iniciar a aplicação de duas formas:

### 1. Rodar pelo Streamlit

**No Windows (PowerShell ou Prompt):**

```Bash
venv\Scripts\activate
streamlit run app.py
```

**No Mac/Linux:**

```Bash
source venv/bin/activate
streamlit run app.py
```

### 2. Rodar como desktop app

Se preferir abrir a interface em uma janela desktop, execute:

**No Windows:**

```Bash
venv\Scripts\activate
python main.py
```

**No Mac/Linux:**

```Bash
source venv/bin/activate
python main.py
```

Se o Streamlit abrir sozinho no navegador, o projeto já está funcionando corretamente.

TODO: futuras instruções e adições sobre o projeto
