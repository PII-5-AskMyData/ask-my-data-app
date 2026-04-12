import os
import json
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Caminhos absolutos para os dados do RAG
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "sap_dictionary.json")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")


def _load_raw_json():
    """Carrega o JSON cru do dicionário SAP."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data():
    """Transforma o dicionário SAP em documentos LangChain para indexação vetorial."""
    data = _load_raw_json()
    docs = []
    for table in data:
        content = f"Tabela SAP: {table['table_name']}\nDescrição: {table['description']}\nCampos:\n"
        for field in table["fields"]:
            content += f"- {field['name']} ({field.get('type', 'N/A')}): {field['description']}\n"
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "table_name": table["table_name"],
                    "description": table["description"],
                },
            )
        )
    return docs


def get_vector_store():
    """Configura e retorna a db de vetores (Chroma) com embeddings do HuggingFace."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    else:
        docs = load_data()
        if docs:
            db = Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_DIR)
        else:
            db = None
    return db


# =============================================================================
#  SCHEMA PREVIEW — retorna dados para exibição da estrutura das tabelas
# =============================================================================
def get_schema_preview():
    """
    Retorna uma lista de dicts, cada um representando uma tabela SAP com suas colunas e tipos.
    Formato: [{"table_name": str, "description": str, "fields": [{"name", "type", "description"}]}]
    """
    data = _load_raw_json()
    return data


def get_schema_dataframe():
    """
    Retorna um DataFrame Pandas único com todas as colunas de todas as tabelas,
    útil para exibição em st.dataframe.
    """
    data = _load_raw_json()
    rows = []
    for table in data:
        for field in table["fields"]:
            rows.append(
                {
                    "Tabela": table["table_name"],
                    "Descrição da Tabela": table["description"],
                    "Coluna": field["name"],
                    "Tipo": field.get("type", "N/A"),
                    "Descrição da Coluna": field["description"],
                }
            )
    return pd.DataFrame(rows)


# =============================================================================
#  GERAÇÃO DE DADOS MOCKADOS PARA GRÁFICOS
# =============================================================================
def _choose_chart_type(query: str):
    """
    Determina o tipo de gráfico mais adequado para a consulta do usuário.
    Retorna: 'bar', 'line', 'area' ou 'scatter'
    """
    q = query.lower()

    # Palavras-chave que indicam mudança ao longo do tempo → line/area
    time_keywords = [
        "mês", "meses", "mes", "ano", "anos", "semana", "dia", "data",
        "período", "periodo", "tempo", "evolução", "evolucao", "tendência",
        "tendencia", "histórico", "historico", "timeline", "crescimento"
    ]
    # Palavras-chave que indicam comparação entre categorias → bar
    compare_keywords = [
        "planta", "centro", "região", "regiao", "tipo", "categoria",
        "comparar", "comparação", "ranking", "top", "maior", "menor",
        "por material", "por fornecedor", "por cliente", "por produto"
    ]
    # Palavras-chave que indicam distribuição / concentração → scatter
    scatter_keywords = [
        "distribuição", "distribuicao", "correlação", "correlacao",
        "dispersão", "dispersao", "relação", "relacao"
    ]

    time_score = sum(1 for k in time_keywords if k in q)
    compare_score = sum(1 for k in compare_keywords if k in q)
    scatter_score = sum(1 for k in scatter_keywords if k in q)

    if scatter_score > time_score and scatter_score > compare_score:
        return "scatter"
    if time_score > compare_score:
        return "line"
    if compare_score > 0:
        return "bar"
    return "bar"  # default


def get_mock_chart_data(query: str):
    """
    Gera dados fictícios para plotar gráficos após a geração do script SQL.
    Retorna: {"chart_type": str, "data": pd.DataFrame, "x": str, "y": str, "title": str}
    """
    import random
    random.seed(42)

    chart_type = _choose_chart_type(query)
    q = query.lower()

    # Cenário: produção ao longo do tempo
    if any(k in q for k in ["mês", "meses", "mes", "período", "periodo", "tempo", "evolução"]):
        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        df = pd.DataFrame(
            {
                "Mês": months,
                "Volume (ton)": [random.randint(800, 2000) for _ in months],
            }
        )
        return {"chart_type": "line" if chart_type == "line" else "area", "data": df, "x": "Mês", "y": "Volume (ton)", "title": "Volume de Produção por Mês"}

    # Cenário: comparação entre centros/plantas
    if any(k in q for k in ["planta", "centro", "fábrica", "fabrica", "unidade"]):
        plants = ["Ortigueira", "Monte Alegre", "Correia Pinto", "Otacílio Costa", "Telêmaco Borba"]
        df = pd.DataFrame(
            {
                "Planta": plants,
                "Produção (ton)": [random.randint(1500, 5000) for _ in plants],
            }
        )
        return {"chart_type": "bar", "data": df, "x": "Planta", "y": "Produção (ton)", "title": "Produção por Planta"}

    # Cenário: faturamento
    if any(k in q for k in ["faturamento", "receita", "vendas", "valor", "netwr"]):
        categories = ["Celulose", "Papel Cartão", "Papelão Ondulado", "Madeira", "Sacos Industriais"]
        df = pd.DataFrame(
            {
                "Segmento": categories,
                "Faturamento (R$ mi)": [random.randint(50, 500) for _ in categories],
            }
        )
        return {"chart_type": "bar", "data": df, "x": "Segmento", "y": "Faturamento (R$ mi)", "title": "Faturamento por Segmento"}

    # Cenário: compras
    if any(k in q for k in ["compra", "pedido", "fornecedor", "preço", "preco"]):
        items = ["Madeira", "Soda Cáustica", "Amido", "Papel Reciclado", "Energia"]
        df = pd.DataFrame(
            {
                "Insumo": items,
                "Custo (R$ mi)": [random.randint(10, 200) for _ in items],
            }
        )
        return {"chart_type": "bar", "data": df, "x": "Insumo", "y": "Custo (R$ mi)", "title": "Custo por Insumo"}

    # Default genérico
    labels = ["Cat A", "Cat B", "Cat C", "Cat D", "Cat E"]
    df = pd.DataFrame(
        {
            "Categoria": labels,
            "Valor": [random.randint(100, 1000) for _ in labels],
        }
    )
    return {"chart_type": chart_type, "data": df, "x": "Categoria", "y": "Valor", "title": "Resultado da Consulta"}


# =============================================================================
#  PROCESSAMENTO PRINCIPAL DA QUERY DO USUARIO
# =============================================================================
def process_user_query(query: str):
    """Função principal chamada pelo Streamlit para orquestrar o agente RAG."""
    db = get_vector_store()

    tables_identified = []
    if db:
        results = db.similarity_search(query, k=2)
        for res in results:
            tables_identified.append(
                {
                    "name": res.metadata.get("table_name", "Desconhecido"),
                    "description": res.metadata.get("description", "Sem descrição"),
                }
            )
    else:
        tables_identified = [{"name": "Erro", "description": "Dicionário de dados não encontrado"}]

    tables_names = [t["name"] for t in tables_identified if t["name"] != "Erro"]

    if "MSEG" in tables_names or "volume de producao" in query.lower() or "produção" in query.lower():
        mock_sql = f"""-- Script SQL Gerado p/ Power BI
-- Intenção Analisada: "{query}"

SELECT 
    WERKS AS "Centro (Planta)",
    MATNR AS "Material",
    SUM(MENGE) AS "Volume de Produção"
FROM 
    MSEG 
WHERE 
    MJAHR = YEAR(GETDATE())
GROUP BY 
    WERKS, 
    MATNR
ORDER BY 
    "Volume de Produção" DESC;"""
    elif "VBRK" in tables_names or "faturamento" in query.lower():
        mock_sql = f"""-- Script SQL Gerado p/ Power BI
-- Intenção Analisada: "{query}"

SELECT 
    FKART AS "Tipo de Faturamento",
    VKORG AS "Organização de Vendas",
    SUM(NETWR) AS "Valor Líquido Total",
    WAERK AS "Moeda"
FROM 
    VBRK 
WHERE 
    FKDAT >= DATEADD(MONTH, -3, GETDATE())
GROUP BY 
    FKART, VKORG, WAERK
ORDER BY 
    "Valor Líquido Total" DESC;"""
    elif "EKPO" in tables_names or "compra" in query.lower():
        mock_sql = f"""-- Script SQL Gerado p/ Power BI
-- Intenção Analisada: "{query}"

SELECT 
    MATNR AS "Material",
    TXZ01 AS "Descrição",
    SUM(MENGE) AS "Qtd Total Comprada",
    AVG(NETPR) AS "Preço Médio"
FROM 
    EKPO
GROUP BY 
    MATNR, TXZ01
ORDER BY 
    "Qtd Total Comprada" DESC;"""
    else:
        tables_str = ", ".join(tables_names) if tables_names else "TABELA"
        mock_sql = f"""-- Script SQL Gerado p/ Power BI
-- Intenção Analisada: "{query}"

SELECT * 
FROM {tables_str}
-- Adapte a cláusula WHERE e campos conforme sua necessidade."""

    chart_info = get_mock_chart_data(query)

    return {
        "tables_identified": tables_identified,
        "generated_script": mock_sql.strip(),
        "script_type": "SQL",
        "chart": chart_info,
    }
