import os
import json
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

 
# Motor do modelo LLM qwen2.5 1.5b
llm = OllamaLLM(model = "qwen2.5-coder:3b", base_url="http://localhost:11434", temperature=0.0)

json_parser = JsonOutputParser()

template_str = """Você é um especialista SAP. Gere a consulta baseada no contexto.
Retorne a resposta EXCLUSIVAMENTE em formato JSON válido, com as seguintes chaves:
- "codigo": contendo o script SQL ou ABAP gerado.
- "explicacao": uma breve explicação de 1 linha sobre o que o código faz.

REGRAS DE OURO:
1. NUNCA invente tabelas ou colunas. Use APENAS o que está listado no Contexto.
2. Por mais que 2 ou mais tabelas aparessam preze pela simplicidade, se em apenas uma tabela você pode responder a necessidade do usuário faça isso, ou seja, não faça joins !
3. Seja eficiente: Se os dados necessários já estiverem na mesma tabela, NÃO faça comandos JOIN.
4. Use a sintaxe SQL padrão (Exemplo: Tabela.Campo). Não use hífen (Tabela-Campo).
5. Se nenhuma tabela for encontrada ou se o usuário falar algo fora do contexto peça desculpas e informe que devido ao erro você não pode fazer nada. 

CONTEXTO: {contexto}
PERGUNTA: {pergunta}

{formato_instrucoes}
"""


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
    """Configura e retorna a db de vetores (Chroma) com coleção explícita"""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    collection_name = "sap_dictionary_nomic_768"


    # Garante que o diretório exista
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    docs = load_data()

    if os.listdir(VECTOR_DB_DIR):
        db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings,
            collection_name=collection_name,
        )
    else:
        if docs:
            db = Chroma.from_documents(
                docs,
                embeddings,
                persist_directory=VECTOR_DB_DIR,
                collection_name=collection_name,
            )
        else:
            db = None

    return db

def process_user_query(query: str):
    """
    Funcao principal chamada pelo Streamlit para orquestrar o agente.
    """
    db = get_vector_store()

    retriver = db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "score_threshold": 0.55,
            "k": 2
        }
    )
    
    tables_identified = []
    if db:
        # Recuperacao semantica por RAG
        # Para fins de demonstracao, pegamos as 2 tabelas mais similares a intencao do usuario
        results = retriver.invoke(query)
        for res in results:
            tables_identified.append({
                "name": res.metadata.get("table_name", "Desconhecido"),
                "description": res.metadata.get("description", "Sem descricao")
            })
    else:
        tables_identified = [{"name": "Erro", "description": "Dicionario de dados nao encontrado"}]
    
    prompt_sap = PromptTemplate.from_template(template= template_str, partial_variables={"contexto":tables_identified,"pergunta":query,"formato_instrucoes": json_parser.get_format_instructions()})

    chain = prompt_sap | llm
    
    response = chain.invoke({})

    return {
        "tables_identified": tables_identified,
        "generated_script": response,
        "script_type": "SQL"
    }