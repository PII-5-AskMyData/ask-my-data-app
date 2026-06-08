import os
import json
from typing import Dict, Iterable, List, Set, Tuple
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
import re
import pandas as pd
import shutil
import unicodedata

# Motor do modelo LLM qwen2.5 1.5b
llm = OllamaLLM(
    model="qwen2.5-coder:7b", base_url="http://localhost:11434", temperature=0.0
)

json_parser = JsonOutputParser()

template_querry = """Você é um Tradutor de Negócios Especialista no ecossistema SAP.
Sua ÚNICA função é pegar a pergunta coloquial do usuário e reescrevê-la substituindo jargões do dia a dia pelos termos técnicos equivalentes das tabelas SAP.

REGRAS ABSOLUTAS:
1. NÃO responda à pergunta. Apenas reescreva a frase.
2. NÃO adicione nenhum texto conversacional (Ex: "Aqui está a tradução", "A pergunta traduzida é"). Retorne APENAS a string traduzida.
3. Se a frase original não tiver jargões que precisem de tradução, retorne a frase original exatamente como foi escrita.

DICIONÁRIO DE DE/PARA (Use isso como base):
- "fábrica", "filial", "unidade", "planta" -> DEVE virar "centro"
- "produto", "peça", "insumo", "mercadoria" -> DEVE virar "material"
- "vendas", "notas fiscais", "receita", "lucro" -> DEVE virar "faturamento" ou "documento de vendas"
- "compras", "aquisição" -> DEVE virar "documento de compras"
- "comprador" -> DEVE virar "cliente"
- "fabricação", "manufatura" -> DEVE virar "produção"
- "envio", "despacho", "transporte" -> DEVE virar "entrega"

--- EXEMPLOS DE COMPORTAMENTO ---

PERGUNTA: "Quero saber o nome da fábrica que teve mais lucro"
TRADUÇÃO: "Quero saber o nome do centro que teve maior faturamento"

PERGUNTA: "Liste as peças compradas pelo nosso melhor comprador"
TRADUÇÃO: "Liste os materiais do documento de compras do nosso melhor cliente"

PERGUNTA: "Qual o maior preço da tabela?"
TRADUÇÃO: "Qual o maior preço da tabela?"

----------------------------------
AGORA É A SUA VEZ:

PERGUNTA: "{user_querry}"
TRADUÇÃO: """

template_sap = """Você é um Arquiteto de Dados SAP sênior.
Sua tarefa é analisar o CONTEXTO, entender a intenção de negócios do usuário e retornar a resposta EXCLUSIVAMENTE em formato JSON válido.



Regras de Ouro para o SQL (Rigor Estrutural):
1. Use APENAS as tabelas e colunas explicitamente listadas no CONTEXTO.
2. NUNCA invente colunas para fazer JOIN.
3. Sempre qualifique todas as colunas com o nome da tabela ou alias (ex: T1.COLUNA).
4. Siga estritamente as "Regras de Relacionamento (JOIN):" descritas no contexto.
5. EXECUÇÃO IMEDIATA: Se você percebeu que precisa fazer um JOIN entre as tabelas do contexto para obter a resposta, FAÇA O CÓDIGO SQL IMEDIATAMENTE. É expressamente PROIBIDO escrever na explicação "seria necessário fazer um JOIN". Se a solução está no contexto, apenas escreva o script na chave "codigo".
6. Se a resposta for genuinamente impossível (tabelas não fornecidas), só então retorne a chave "codigo" vazia e explique de forma educada e intuitiva o porquê na chave "explicacao".


Regras de Interpretação (Flexibilidade Semântica):
7. SEJA INTELIGENTE COM SINÔNIMOS: O usuário é de negócios. Entenda que "compra" é o mesmo que "pedido de compra", "estoque" é o mesmo que "quantidade disponível", "fábrica" é "centro". Conecte o termo da pergunta à coluna que faz mais sentido no contexto.

---
INSTRUCOES PARA VISUALIZACAO:
- Na chave "visualizacoes": Você pode gerar uma lista gerar de 0 a 4 gráficos. SEJA DIVERSIFICADO. Não use apenas o mesmo gráfico.
- Dentro de cada item da lista, preencha:
  - "tipo_grafico":Siga esta regra lógica:
    * Use 'bar' para comparar volumes/categorias.
    * Use 'line' ou 'area' para tendências ao longo do tempo.
    * Use 'pie' para representar fatias/distribuição de um todo.
  - "cenario": Escolha entre: 'producao', 'faturamento', 'compras', 'comparacao', 'evolucao', 'distribuicao'.
  - "titulo": Um título curto e elegante.

---
EXEMPLOS DE COMPORTAMENTO (FEW-SHOT):

Usuário: "Qual o número do depósito complexo e a quantidade disponível no local físico com o maior estoque?"
SQL: SELECT LGNUM, VERME FROM LQUA ORDER BY VERME DESC LIMIT 1;

Usuário: "Qual o número do material com o menor estoque de utilização livre e a data de fabricação do lote?"
SQL: SELECT MCHB.MATNR, MCHA.HSDAT, MCHB.CLABS FROM MCHB JOIN MCHA ON MCHB.MATNR = MCHA.MATNR AND MCHB.WERKS = MCHA.WERKS AND MCHB.CHARG = MCHA.CHARG ORDER BY MCHB.CLABS ASC LIMIT 1;

Usuário: "Quero saber o nome do cliente e o número do material vendido para o item com a maior quantidade desejada."
SQL: SELECT KNA1.NAME1, VBAP.MATNR FROM VBAP JOIN VBAK ON VBAP.VBELN = VBAK.VBELN JOIN KNA1 ON VBAK.KUNNR = KNA1.KUNNR ORDER BY VBAP.ZMENG DESC LIMIT 1;

---
CONTEXTO: {contexto}
PERGUNTA: {pergunta}

{formato_instrucoes}
"""


# Caminhos absolutos para os dados do RAG
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "sap_dictionary_v2.json")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Tunables for retrieval and validation
ENABLE_TRANSLATION = False
SEMANTIC_K = 12
BM25_K = 10
MAX_TABLES_RETRIEVED = 12
MIN_TABLES_CONTEXT = 4
MAX_TABLES_CONTEXT = 6



def load_data():
    """Carrega o dicionario SAP mockado em memoria otimizado para Semântica."""
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for table in data:
        nome_tabela = table["table_name"]
        descricao = table["description"]

        # 1. Extraímos apenas os significados de negócio dos campos (Sem ruído de VARCHAR)
        descricoes_de_negocio = [field["description"] for field in table["fields"]]
        resumo_campos = ", ".join(descricoes_de_negocio)

        # 2. Montamos o texto dando PESO EXTREMO aos assuntos que a tabela resolve
        content = f"Tabela SAP: {nome_tabela}\n"
        content += f"Descrição Geral: {descricao}\n"
        content += f"Assuntos, dados e colunas que esta tabela possui: {resumo_campos}\n\n"

        # 3. Listamos o técnico por último (para o 7B ler na hora de montar o SQL)
        content += "Mapeamento Técnico (Campos):\n"
        for field in table["fields"]:
            content += f"- {field['name']} ({field.get('type', '')}): {field['description']}\n"

        docs.append(
            Document(
                page_content=content,
                metadata={
                    "table_name": nome_tabela,
                    "description": descricao
                },
            )
        )
    return docs


def get_vector_store():
    """Configura e retorna a db de vetores (Chroma) com coleção explícita"""
    embeddings = OllamaEmbeddings(model="bge-m3")
    collection_name = "sap_dictionary_bgem3_1024"

    # Garante que o diretório exista
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    docs = load_data()

    if os.listdir(VECTOR_DB_DIR):
        db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings,
            collection_name=collection_name,
        )
        if db._collection.count() != len(docs):
            print("Atualizacao detectada no JSON. Recriando o banco Vetorial...")
            shutil.rmtree(VECTOR_DB_DIR)
            os.makedirs(VECTOR_DB_DIR, exist_ok=True)
            db = Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_DIR, collection_name=collection_name)
    else:
        if docs:
            print("Criando o banco vetorial...")
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


def _normalize_text(text: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )


def _tokenize_basic(text: str) -> List[str]:
    normalized = _normalize_text(text)
    tokens = re.findall(r"\b\w+\b", normalized)
    return [token for token in tokens if len(token) > 2]


def _add_join_rule(
    join_rules: Dict[Tuple[str, str], Set[str]], table_a: str, table_b: str, column: str
):
    join_rules.setdefault((table_a, table_b), set()).add(column)
    join_rules.setdefault((table_b, table_a), set()).add(column)


def _build_schema_index() -> Dict[str, Dict[str, Set[str]]]:
    data = _load_raw_json()
    table_columns: Dict[str, Set[str]] = {}
    table_descriptions: Dict[str, str] = {}
    join_rules: Dict[Tuple[str, str], Set[str]] = {}
    token_index: Dict[str, Dict[str, Set[str]]] = {}
    token_df: Dict[str, int] = {}
    table_tokens: Dict[str, Set[str]] = {}
    table_ngrams: Dict[str, Set[str]] = {}
    ngram_df: Dict[str, int] = {}

    for table in data:
        table_name = str(table.get("table_name", "")).upper()
        if not table_name:
            continue

        description = str(table.get("description", ""))
        table_descriptions[table_name] = description

        columns = {
            str(field.get("name", "")).upper()
            for field in table.get("fields", [])
            if field.get("name")
        }
        table_columns[table_name] = columns

        table_name_tokens = set(_tokenize_basic(table_name))
        table_desc_tokens = set(_tokenize_basic(description))
        field_name_tokens: Set[str] = set()
        field_desc_tokens: Set[str] = set()
        text_parts = [table_name, description]
        for field in table.get("fields", []):
            field_name = str(field.get("name", ""))
            field_desc = str(field.get("description", ""))
            field_name_tokens.update(_tokenize_basic(field_name))
            field_desc_tokens.update(_tokenize_basic(field_desc))
            text_parts.append(field_name)
            text_parts.append(field_desc)

        token_index[table_name] = {
            "table_name": table_name_tokens,
            "table_desc": table_desc_tokens,
            "field_name": field_name_tokens,
            "field_desc": field_desc_tokens,
        }

        token_list = _tokenize_basic(" ".join(text_parts))
        token_set = set(token_list)
        table_tokens[table_name] = token_set

        ngrams = set()
        ngrams |= _extract_ngrams(token_list, 2)
        ngrams |= _extract_ngrams(token_list, 3)
        table_ngrams[table_name] = ngrams

        for token in token_set:
            token_df[token] = token_df.get(token, 0) + 1
        for ngram in ngrams:
            ngram_df[ngram] = ngram_df.get(ngram, 0) + 1

        join_rules_text = str(table.get("join_rules", ""))

        for match in re.finditer(
            r"Liga com\s+([A-Z0-9_]+)\s+usando.*?\b([A-Z0-9_]+)\b",
            join_rules_text,
            flags=re.IGNORECASE,
        ):
            other_table = match.group(1).upper()
            column = match.group(2).upper()
            _add_join_rule(join_rules, table_name, other_table, column)

    return {
        "columns": table_columns,
        "descriptions": table_descriptions,
        "join_rules": join_rules,
        "token_index": token_index,
        "token_df": token_df,
        "table_tokens": table_tokens,
        "table_ngrams": table_ngrams,
        "ngram_df": ngram_df,
    }


def _truncate_text(text: str, max_len: int = 420) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."



def _build_context_from_tables(
    table_names: List[str], schema_index: Dict[str, Dict[str, Set[str]]]
) -> str:
    # 1. Carregamos o JSON cru para resgatar as descrições das colunas
    raw_data = _load_raw_json()
    raw_dict = {str(t["table_name"]).upper(): t for t in raw_data}

    table_columns = schema_index["columns"]
    table_descriptions = schema_index["descriptions"]

    lines: List[str] = []
    for table in table_names:
        description = _truncate_text(table_descriptions.get(table, ""))

        lines.append(f"Tabela: {table}")
        lines.append(f"Descricao: {description}")
        
        # ================= NOVO BLOCO DE CONTEXTO =================
        # Entrega as regras matemáticas mastigadas para o LLM
        if table in raw_dict:
            regras_join = raw_dict[table].get("join_rules", "")
            if regras_join:
                lines.append(f"Regras de Relacionamento (JOIN): {regras_join}")
                
            lines.append("Colunas Detalhadas:")
            for field in raw_dict[table].get("fields", []):
                c_name = field.get("name", "")
                c_desc = field.get("description", "")
                c_type = field.get("type", "")
                lines.append(f"  - {c_name} ({c_type}): {c_desc}")
        else:
            # Fallback
            columns = sorted(table_columns.get(table, set()))
            lines.append(f"Colunas: {', '.join(columns)}")
        # ==========================================================

        lines.append("")

    return "\n".join(lines).strip()


def _find_table_mentions(query: str, table_names: Iterable[str]) -> List[str]:
    tokens = re.findall(r"\b[A-Z0-9_]{3,}\b", query.upper())
    table_set = set(table_names)
    mentions = [token for token in tokens if token in table_set]
    return sorted(set(mentions))


def _extract_ngrams(tokens: List[str], size: int) -> Set[str]:
    if size <= 1 or len(tokens) < size:
        return set()
    return {" ".join(tokens[i : i + size]) for i in range(len(tokens) - size + 1)}


def _select_tables_for_context(
    query: str,
    candidates: List[Document],
    schema_index: Dict[str, Dict[str, Set[str]]],
) -> List[str]:
    """
    Seleciona as tabelas respeitando estritamente o ranking gerado pelo 
    EnsembleRetriever (BM25 + Chroma), sem recálculos redundantes.
    """
    selected_tables = []
    seen = set()

    # 1. Prioridade Máxima: Tabelas citadas explicitamente pelo usuário na pergunta (Regex)
    forced_tables = _find_table_mentions(query, schema_index["columns"].keys())
    for table in forced_tables:
        if table not in seen:
            selected_tables.append(table)
            seen.add(table)

    # 2. Respeita a inteligência do RAG: Pega na ordem exata que o motor trouxe
    for doc in candidates:
        table_name = str(doc.metadata.get("table_name", "")).upper()
        if not table_name or table_name in seen:
            continue
            
        selected_tables.append(table_name)
        seen.add(table_name)

        # Corta no limite estabelecido para não estourar a memória do LLM (7B)
        if len(selected_tables) >= MAX_TABLES_CONTEXT:
            break

    return selected_tables



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

def limpar_texto(texto):
    """Remove acentos, joga para minúsculo e elimina 'stop words' e pontuações."""
    # Garante que é string e minúscula
    texto = str(texto).lower()
    
    # Remove acentos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    
    # Extrai apenas as palavras (ignora vírgulas, pontos, parênteses)
    palavras = re.findall(r'\b\w+\b', texto)
    
    # O "Veneno" contra as tabelas falsas (Stop Words do Português)
    stop_words = {
        'o', 'a', 'os', 'as', 'do', 'da', 'dos', 'das', 'de', 'di', 'du', 
        'para', 'que', 'e', 'em', 'um', 'uma', 'uns', 'umas', 'com', 
        'no', 'na', 'nos', 'nas', 'por', 'teve', 'saber', 'gostaria'
    }
    
    # Mantém apenas as palavras que trazem significado real para a busca
    palavras_uteis = [p for p in palavras if p not in stop_words]
    
    return palavras_uteis

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
        df = pd.DataFrame(
            {
                "Planta": plants,
                "Produção (ton)": [random.randint(1500, 5000) for _ in plants],
            }
        )
        return {
            "chart_type": tipo_grafico,
            "data": df,
            "x": "Planta",
            "y": "Produção (ton)",
            "title": titulo_ia,
        }

    # Cenário: comparação entre centros/plantas
    if cenario == "comparacao":
        plants = [
            "Ortigueira",
            "Monte Alegre",
            "Correia Pinto",
            "Otacílio Costa",
            "Telêmaco Borba",
        ]
        df = pd.DataFrame(
            {
                "Planta": plants,
                "Produção (ton)": [random.randint(1500, 5000) for _ in plants],
            }
        )
        return {
            "chart_type": tipo_grafico,
            "data": df,
            "x": "Planta",
            "y": "Produção (ton)",
            "title": titulo_ia,
        }

    # Cenário: faturamento
    if cenario == "faturamento":
        categories = ["Celulose", "Papel Cartão", "Papelão Ondulado"]
        df = pd.DataFrame(
            {
                "Segmento": categories,
                "Faturamento (R$ mi)": [random.randint(50, 500) for _ in categories],
            }
        )
        return {
            "chart_type": tipo_grafico,
            "data": df,
            "x": "Segmento",
            "y": "Faturamento (R$ mi)",
            "title": titulo_ia,
        }

    # Cenário: compras
    if cenario == "compras":
        items = ["Madeira", "Soda Cáustica", "Amido", "Papel Reciclado", "Energia"]
        df = pd.DataFrame(
            {
                "Insumo": items,
                "Custo (R$ mi)": [random.randint(10, 200) for _ in items],
            }
        )
        return {
            "chart_type": tipo_grafico,
            "data": df,
            "x": "Insumo",
            "y": "Custo (R$ mi)",
            "title": titulo_ia,
        }

   # Cenário: evolução temporal (Força a IA a usar 'line' ou 'area')
    if cenario == "evolucao":
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        # Cria uma linha de tendência crescente com uma leve variação
        df = pd.DataFrame(
            {
                "Mês": meses,
                "Volume": [random.randint(100, 300) + (i * 50) for i in range(6)],
            }
        )
        return {
            "chart_type": tipo_grafico,
            "data": df,
            "x": "Mês",
            "y": "Volume",
            "title": titulo_ia,
        }

    # Cenário: distribuição/status (Força a IA a pensar em 'pie' ou proporções)
    if cenario == "distribuicao":
        status = ["Entregue", "Em Trânsito", "Atrasado", "Cancelado"]
        df = pd.DataFrame(
            {
                "Status": status,
                "Quantidade": [
                    random.randint(500, 1000), 
                    random.randint(100, 300), 
                    random.randint(10, 50), 
                    random.randint(0, 20)
                ],
            }
        )
        return {
            "chart_type": tipo_grafico,
            "data": df,
            "x": "Status",
            "y": "Quantidade",
            "title": titulo_ia,
        }



def _build_error_result(message: str, translated_query: str) -> dict:
    return {
        "error": True,
        "error_message": message,
        "tables_identified": [],
        "generated_script": "",
        "explanation": "",
        "chart": None,
        "script_type": "SQL",
        "translated_query": translated_query,
    }


def translate_to_sap(user_querry: str) -> str:
    """
    Pré-processa a string do usuário traduzindo jargões de negócio
    para a nomenclatura padrão descrita no schema do SAP.
    """
    try:

        translate_prompt = PromptTemplate.from_template(
            template=template_querry,
        )

        chain_traducao = translate_prompt | llm

        refected_user_query = chain_traducao.invoke({"user_querry": user_querry})

    except Exception as e:
        print(f"Erro ao processar a resposta da IA: {e}")
        return user_querry

    return refected_user_query


def process_user_query(query: str):
    """Função principal chamada pelo Streamlit para orquestrar o agente RAG."""
    translated_query = translate_to_sap(user_querry=query) if ENABLE_TRANSLATION else query

    try:
        db = get_vector_store()

        if db is None:
            return _build_error_result(
                "O dicionário SAP local não está disponível. Verifique se o arquivo data/sap_dictionary.json existe e tente novamente.",
                translated_query,
            )

        chorma_retriver = db.as_retriever(
            search_type="similarity",
            search_kwargs={
                # "score_threshold": 0.35,
                "k": SEMANTIC_K,
                # "fetch_k": 20,
                # "lambda_mult": 0.40
            },
        )

        docs = load_data()

        bm25_retriver = BM25Retriever.from_documents(documents=docs, preprocess_func=limpar_texto)
        bm25_retriver.k = BM25_K

        ensemble_retriver = EnsembleRetriever(
            retrievers=[bm25_retriver, chorma_retriver],
            weights= [0.5,0.5]
        )

        schema_index = _build_schema_index()
        tables_identified = []

        doc_by_table = {
            str(doc.metadata.get("table_name", "")).upper(): doc
            for doc in docs
            if doc.metadata.get("table_name")
        }

        # Recuperacao semantica por RAG
        results = ensemble_retriver.invoke(translated_query)
        results_bm25 = bm25_retriver.invoke(translated_query)
        combined_results = []
        seen_tables = set()
        for res in results + results_bm25:
            table_name = str(res.metadata.get("table_name", "")).upper()
            if not table_name or table_name in seen_tables:
                continue
            combined_results.append(res)
            seen_tables.add(table_name)
            if len(combined_results) >= MAX_TABLES_RETRIEVED:
                break

        forced_tables = _find_table_mentions(translated_query, schema_index["columns"].keys())
        for table in forced_tables:
            if table in seen_tables or table not in doc_by_table:
                continue
            if len(combined_results) >= MAX_TABLES_RETRIEVED:
                break
            combined_results.append(doc_by_table[table])
            seen_tables.add(table)

        table_names = _select_tables_for_context(
            translated_query, combined_results, schema_index
        )
        if not table_names:
            return _build_error_result(
                "Nao foi possivel identificar tabelas relevantes no dicionario SAP.",
                translated_query,
            )

        for table in table_names:
            tables_identified.append(
                {
                    "name": table,
                    "description": schema_index["descriptions"].get(table, "Sem descricao"),
                    "tags": "Sem tag",
                }
            )

        final_ia_context = _build_context_from_tables(table_names, schema_index)

        print(final_ia_context)

        try:
            prompt_sap = PromptTemplate.from_template(
                template=template_sap,
                partial_variables={
                    "contexto": final_ia_context,
                    "formato_instrucoes": json_parser.get_format_instructions(),
                    },
            )

            chain = prompt_sap | llm | json_parser
            response = chain.invoke(query)
        except ConnectionError:
            return _build_error_result(
                "Nao foi possivel conectar ao Ollama. Verifique se o servico esta em execucao e tente novamente.",
                translated_query,
            )
        except Exception as e:
            print(f"Erro ao processar a resposta da IA: {e}")
            return _build_error_result(
                "A IA nao conseguiu gerar a consulta agora. Tente novamente em instantes.",
                translated_query,
            )

        lista_visualizacoes = response.get("visualizacoes", [])


        charts_data = []

        for vis in lista_visualizacoes:
            cenario_ia = vis.get("cenario", "comparacao")
            tipo_ia = vis.get("tipo_grafico", "bar")
            titulo_ia = vis.get("titulo", "Dashboard Dinâmico")
            
            chart = get_chart_data(cenario=cenario_ia, tipo_grafico=tipo_ia, titulo_ia=titulo_ia)
            charts_data.append(chart)
        
        print("Charts data: ", charts_data)
        return {
            "tables_identified": tables_identified,
            "generated_script": response.get("codigo", ""),
            "explanation": response.get("explicacao", ""),
            "charts": charts_data,
            "visualizacoes": lista_visualizacoes,
            "script_type": "SQL",
            "translated_query": translated_query,
        }
    except ConnectionError:
        return _build_error_result(
            "Não foi possível conectar ao Ollama. Verifique se o serviço está em execução e tente novamente.",
            translated_query,
        )
    except Exception as e:
        print(f"Erro inesperado ao processar a consulta: {e}")
        return _build_error_result(
            "Ocorreu um erro ao processar sua consulta. Tente novamente.",
            translated_query,
        )
