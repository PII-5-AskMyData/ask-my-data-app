import os
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Caminhos absolutos para os dados do RAG
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "sap_dictionary.json")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

def load_data():
    """Carrega o dicionario SAP mockado em memoria."""
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    docs = []
    for table in data:
        # Texto sendo indexado no banco vetorial
        content = f"Tabela SAP: {table['table_name']}\nDescricao: {table['description']}\nCampos:\n"
        for field in table['fields']:
            content += f"- {field['name']}: {field['description']}\n"
        
        docs.append(Document(
            page_content=content, 
            metadata={
                "table_name": table["table_name"], 
                "description": table["description"]
            }
        ))
    return docs

def get_vector_store():
    """Configura e retorna a db de vetores (Chroma) carregada com embedder do HuggingFace"""
    # Modelo local leve para gerar o embedding (Sentence Transformers)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Se ja existir a DB local e não estiver vazia
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    else:
        # Carregar pela primeira vez
        docs = load_data()
        if docs:
            db = Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_DIR)
        else:
            db = None
    return db

def process_user_query(query: str):
    """
    Funcao principal chamada pelo Streamlit para orquestrar o agente.
    """
    db = get_vector_store()
    
    tables_identified = []
    if db:
        # Recuperacao semantica por RAG
        # Para fins de demonstracao, pegamos as 2 tabelas mais similares a intencao do usuario
        results = db.similarity_search(query, k=2)
        for res in results:
            tables_identified.append({
                "name": res.metadata.get("table_name", "Desconhecido"),
                "description": res.metadata.get("description", "Sem descricao")
            })
    else:
        tables_identified = [{"name": "Erro", "description": "Dicionario de dados nao encontrado"}]
        
    
    # IMPORTANTE: Aqui integrariamos com o LLM da empresa (Ex: OpenAI, Azure, Gemini, local)
    # usando langchain para receber os chunks recuperados acima e gerar a string SQL.
    # Exemplo mockado baseado nas tabelas encontradas para o inicio do projeto:
    
    tables_names = [t["name"] for t in tables_identified if t["name"] != "Erro"]
    
    if "MSEG" in tables_names or "volume de producao" in query.lower():
        mock_sql = f"""-- Script SQL Gerado p/ Power BI
-- Intencao Analisada: "{query}"

SELECT 
    WERKS AS "Centro (Planta)",
    MATNR AS "Material",
    SUM(MENGE) AS "Volume de Producao"
FROM 
    MSEG 
WHERE 
    MJAHR = YEAR(GETDATE()) -- Ex: Ultimos 3 meses
GROUP BY 
    WERKS, 
    MATNR
ORDER BY 
    "Volume de Producao" DESC;
        """
    else:
        tables_str = ", ".join(tables_names) if tables_names else "TABELA_MOCK"
        mock_sql = f"""-- Script SQL Gerado p/ Power BI
-- Intencao Analisada: "{query}"

SELECT * 
FROM {tables_str}
-- (Adapte a clausula WHERE e campos para sua necessidade)
"""

    return {
        "tables_identified": tables_identified,
        "generated_script": mock_sql.strip(),
        "script_type": "SQL"
    }
