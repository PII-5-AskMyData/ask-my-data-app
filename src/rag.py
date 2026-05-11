import os
import json
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import re
import pandas as pd


 
# Motor do modelo LLM qwen2.5 1.5b
llm = OllamaLLM(model = "qwen2.5-coder:3b", base_url="http://localhost:11434", temperature=0.0)

json_parser = JsonOutputParser()

template_str = """Você é um especialista SAP. Gere a consulta baseada no contexto fornecido.
Retorne a resposta EXCLUSIVAMENTE em formato JSON válido, com as seguintes chaves:
- "codigo": contendo o script SQL gerado.
- "explicacao": uma breve explicação de 1 linha sobre o que o código faz.
- "visualizacao (basei-se no SQL gerado para escolher a melhor opção)": objeto contendo:
    * "tipo_grafico": (escolha entre 'bar', 'line', 'area', 'pie')
    * "cenario": (escolha entre 'producao', 'faturamento', 'compras', 'comparacao')
    * "titulo": Um título elegante para o gráfico.

REGRAS DE OURO:
1. NUNCA invente tabelas ou colunas. Use APENAS as tabelas e os campos listados no Contexto abaixo.
2. UTILIZE O MÍNIMO DE TABELAS NECESSÁRIAS. Analise cada uma e ignore as que não possuem relação com a pergunta.
3. RELACIONAMENTO (JOIN): Se a pergunta pedir cruzamento de dados (ex: Produção e Centro) e eles estiverem em tabelas diferentes no Contexto, FAÇA UM JOIN utilizando a coluna em comum (ex: AUFNR).
4. Use a sintaxe SQL padrão (Exemplo: Tabela.Campo).
5. Se não houver como relacionar as tabelas fornecidas para responder à pergunta, retorne a chave "codigo" vazia e explique o porquê.

CONTEXTO: {contexto}
PERGUNTA: {pergunta}

{formato_instrucoes}
"""


# Caminhos absolutos para os dados do RAG
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "sap_dictionary.json")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

TAGS_PER_TABLE = {
    "MSEG": "movimentação, estoque, centro, planta, material, filial, local",
    "AFKO": "produção, fabricação, ordem, quantidade, manufatura",
    "VBRK": "faturamento, vendas, notas fiscais, receita",
    "EKPO": "compras, pedido, aquisição, suprimentos",
    "MARA": "produto, item, peça, mercadoria",
    "LIKP": "entrega, envio, despacho, transporte"
}

def load_data():
    """Carrega o dicionario SAP mockado em memoria."""
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    docs = []
    for table in data:
        nome_tabela = table['table_name']
        
        # Busca as tags dinamicamente pelo nome da tabela
        tags_dinamicas = TAGS_PER_TABLE.get(nome_tabela, "")
        
        # Monta o texto para o vetor
        content = f"Tabela SAP: {nome_tabela}\n"
        content += f"Descrição: {table['description']}\n"
        
        if tags_dinamicas:
             content += f"Palavras-chave e Sinônimos (Negócio): {tags_dinamicas}\n"
             
        content += "Campos:\n"
        for field in table['fields']:
            content += f"- {field['name']}: {field['description']}\n"
        
        docs.append(Document(
            page_content=content, 
            metadata={
                "table_name": nome_tabela, 
                "description": table["description"],
                "tags": tags_dinamicas # Salva no metadata para uso futuro
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

# =============================================================================
#  SCHEMA PREVIEW — retorna dados para exibição da estrutura das tabelas
# =============================================================================
def _load_raw_json():
    """Lê o arquivo JSON e retorna a lista de dicionários original."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_schema_preview():
    """
    Retorna a estrutura original do dicionário SAP para uso na UI.
    Formato: [{"table_name": str, "description": str, "fields": [...]}]
    """
    # Chamamos o carregador bruto, que já devolve exatamente 
    # o formato que a docstring exige.
    return _load_raw_json()

def get_schema_dataframe():
    data = _load_raw_json() 
    rows = []
    for table in data:
        # Aqui table é um dicionário real do JSON
        for field in table["fields"]:
            rows.append({
                "Tabela": table["table_name"],
                "Descrição da Tabela": table["description"],
                "Coluna": field["name"],
                "Tipo": field.get("type", "N/A"),
                "Descrição da Coluna": field["description"],
            })
    return pd.DataFrame(rows)

# =============================================================================
#  CHART DATA — A PARTIR DO CENÁRIO A IA ESCOLHE O MELHOR TIPO DE GRÁFICO
# =============================================================================
def get_chart_data(cenario: str, tipo_grafico: str, titulo_ia: str):
    """
    Gera dados fictícios para plotar gráficos após a geração do script SQL.
    Retorna: {"chart_type": str, "data": pd.DataFrame, "x": str, "y": str, "title": str}
    """
    import random
    random.seed(42)

    # Cenário: produção ao longo do tempo
    if cenario == "producao":
        plants = ["Ortigueira", "Monte Alegre", "Correia Pinto", "Otacílio Costa"]
        df = pd.DataFrame({
            "Planta": plants,
            "Produção (ton)": [random.randint(1500, 5000) for _ in plants]
        })
        return {"chart_type": tipo_grafico, "data": df, "x": "Planta", "y": "Produção (ton)", "title": titulo_ia}

    # Cenário: comparação entre centros/plantas
    if cenario == 'comparacao':
        plants = ["Ortigueira", "Monte Alegre", "Correia Pinto", "Otacílio Costa", "Telêmaco Borba"]
        df = pd.DataFrame(
            {
                "Planta": plants,
                "Produção (ton)": [random.randint(1500, 5000) for _ in plants],
            }
        )
        return {"chart_type": tipo_grafico, "data": df, "x": "Planta", "y": "Produção (ton)", "title": titulo_ia}

    # Cenário: faturamento
    if cenario == "faturamento":
        categories = ["Celulose", "Papel Cartão", "Papelão Ondulado"]
        df = pd.DataFrame({
            "Segmento": categories,
            "Faturamento (R$ mi)": [random.randint(50, 500) for _ in categories]
        })
        return {"chart_type": tipo_grafico, "data": df, "x": "Segmento", "y": "Faturamento (R$ mi)", "title": titulo_ia}

    # Cenário: compras
    if cenario == "compras":
        items = ["Madeira", "Soda Cáustica", "Amido", "Papel Reciclado", "Energia"]
        df = pd.DataFrame(
            {
                "Insumo": items,
                "Custo (R$ mi)": [random.randint(10, 200) for _ in items],
            }
        )
        return {"chart_type": tipo_grafico, "data": df, "x": "Insumo", "y": "Custo (R$ mi)", "title": titulo_ia}
    
    # TODO
    # Adicionar mais cenários

    # Default genérico
    df = pd.DataFrame({"Categoria": ["A", "B", "C"], "Valor": [10, 20, 30]})
    
    return {"chart_type": tipo_grafico, "data": df, "x": "Categoria", "y": "Valor", "title": titulo_ia}

def translate_to_sap(user_querry: str) -> str:
    """
    Pré-processa a string do usuário traduzindo jargões de negócio 
    para a nomenclatura padrão descrita no schema do SAP.
    """
    
    # Dicionário de Regex mapeando (Padrão de Negócio -> Termo do Schema SAP)
    # O \b garante que apenas a palavra exata seja substituída (word boundaries)
    dicionario_sap = {
        # --- Localidades / Plantas ---
        r'\bplantas?\b': 'centro',
        r'\bf[áa]bricas?\b': 'centro',
        r'\bfilia(l|is)\b': 'centro',
        r'\bunidades?\b': 'centro',

        # --- Materiais / Produtos ---
        r'\bprodutos?\b': 'material',
        r'\bitens?\b': 'material',
        r'\bpe[çc]as?\b': 'material',
        r'\bmercadorias?\b': 'material',
        r'\binsumos?\b': 'material',

        # --- Quantidade / Medidas ---
        r'\bvolumes?\b': 'quantidade',
        r'\bmontantes?\b': 'quantidade',

        # --- Vendas / Faturamento ---
        r'\bvendas?\b': 'faturamento',
        r'\bnotas? fiscais\b': 'faturamento',
        r'\bnfs?\b': 'faturamento',
        r'\breceitas?\b': 'faturamento',
        r'\bcomprador(es)?\b': 'cliente',

        # --- Compras / Suprimentos ---
        r'\bcompras?\b': 'documento de compras',
        r'\bpedidos? (de )?compra\b': 'documento de compras',
        r'\baquisi[çc][ãa]o\b': 'documento de compras',
        r'\bfornecedor(es)?\b': 'fornecedor', # Caso expanda o schema para LFA1

        # --- Produção ---
        r'\bfabrica[çc][ãa]o\b': 'produção',
        r'\bmanufatura\b': 'produção',

        # --- Logística / Entregas ---
        r'\benvios?\b': 'entrega',
        r'\bdespachos?\b': 'entrega',
        r'\btransportes?\b': 'entrega'
    }

    pergunta_traduzida = user_querry.lower()

    for padrao, termo_sap in dicionario_sap.items():
        pergunta_traduzida = re.sub(padrao, termo_sap, pergunta_traduzida)

    return pergunta_traduzida


def process_user_query(query: str):
    """Função principal chamada pelo Streamlit para orquestrar o agente RAG."""
    db = get_vector_store()

    refected_user_query = translate_to_sap(user_querry=query)
    print("Pergunta traduzida: ", refected_user_query)

    retriver = db.as_retriever(
        search_type="similarity",
        search_kwargs={
            # "score_threshold": 0.55,
            "k": 3,
            # "fetch_k": 15,
            # "lambda_mult": 0.65
        }
    )
    
    tables_identified = []
    text_for_context = []
    if db:
        # Recuperacao semantica por RAG
        results = retriver.invoke(refected_user_query)
        for res in results:
            tables_identified.append(
                {
                    "name": res.metadata.get("table_name", "Desconhecido"),
                    "description": res.metadata.get("description", "Sem descrição"),
                    "tags": res.metadata.get("tags", "Sem tag")
                }
            )
            text_for_context.append(res.page_content)
        final_ia_context = "\n\n".join(text_for_context)
    else:
        tables_identified = [{"name": "Erro", "description": "Dicionario de dados nao encontrado"}]
        final_ia_context = "Dicionário de dados não encontrado."
   
   

    prompt_sap = PromptTemplate.from_template(template= template_str, partial_variables={"contexto":final_ia_context,"pergunta":refected_user_query,"formato_instrucoes": json_parser.get_format_instructions()})

    chain = prompt_sap | llm | json_parser

    try:
        response = chain.invoke({})
    except Exception as e:
        # Caso o Qwen 3B gere um JSON inválido
        print(f"Erro ao parsear JSON: {e}")
        response = {
            "codigo": "",
            "explicacao": "Erro de formatação na resposta da IA.",
            "visualizacao": {"tipo_grafico": "bar", "cenario": "default", "titulo": "Erro"}
        }

    viz_config = response.get("visualizacao", {})
    cenario_ia = viz_config.get("cenario", "default")
    tipo_ia = viz_config.get("tipo_grafico", "bar")
    titulo_ia = viz_config.get("titulo", "Análise de Dados")

    chart = get_chart_data(
        cenario=cenario_ia, 
        tipo_grafico=tipo_ia, 
        titulo_ia=titulo_ia
    )

    return {
        "tables_identified": tables_identified,
        "generated_script": response.get("codigo", ""), 
        "explanation": response.get("explicacao", ""),
        "chart": chart, 
        "script_type": "SQL"
    }
