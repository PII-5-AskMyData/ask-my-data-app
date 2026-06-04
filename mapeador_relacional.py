import json
import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "sap_dictionary.json")

# Campos administrativos do SAP que ignoramos para não gerar falsos JOINs
CAMPOS_IGNORADOS = {"MANDT", "ERDAT", "ERNAM", "AEDAT", "AENAM", "SPRAS"}

# Temperatura 0.1 para a IA ser puramente técnica e não inventar histórias
llm = OllamaLLM(model="qwen2.5-coder:7b", base_url="http://localhost:11434", temperature=0.1)

template_join = """Você é um Arquiteto de Dados SAP.
Identificamos duas tabelas que possuem uma coluna em comum. Sua tarefa é analisar se faz sentido comercial e técnico uni-las.

Tabela A: {tabela_a} - {desc_a}
Tabela B: {tabela_b} - {desc_b}
Coluna em comum: {coluna}

Se fizer sentido juntar as duas para um relatório, responda APENAS com a regra, usando ESTE FORMATO EXATO:
"REGRAS DE JOIN: Liga com {tabela_b} usando a chave {coluna} para obter dados de [explique o motivo em 3 palavras]."

Se não fizer sentido de negócio cruzar essas duas tabelas, responda APENAS a palavra: NENHUMA.

Regra:"""

prompt_join = PromptTemplate(template=template_join, input_variables=["tabela_a", "desc_a", "tabela_b", "desc_b", "coluna"])
chain = prompt_join | llm

def mapear_relacionamentos():
    if not os.path.exists(DATA_FILE):
        print("Arquivo JSON não encontrado.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        tabelas = json.load(f)

    # Passo 1: Extrair todas as colunas de todas as tabelas
    mapa_colunas = {} # { "KUNNR": ["KNA1", "LIKP", "VBAK"] }
    for tab in tabelas:
        nome_tab = tab["table_name"]
        for campo in tab.get("fields", []):
            col_name = campo["name"]
            if col_name not in CAMPOS_IGNORADOS:
                if col_name not in mapa_colunas:
                    mapa_colunas[col_name] = []
                mapa_colunas[col_name].append(nome_tab)

    print("Mapa de chaves estrangeiras montado. Iniciando inferência com IA...")
    modificacoes = 0

    # Passo 2: Analisar os cruzamentos possíveis
    for coluna, lista_tabelas in mapa_colunas.items():
        # Só analisa se a coluna existir em 2 ou mais tabelas
        if len(lista_tabelas) > 1 and len(lista_tabelas) < 10: 
            # (Filtro < 10 para evitar analisar colunas genéricas demais tipo BUKRS que estariam em 40 tabelas)
            
            # Pega as combinações (Ex: KNA1 com LIKP)
            for i in range(len(lista_tabelas)):
                for j in range(i + 1, len(lista_tabelas)):
                    tab_a = lista_tabelas[i]
                    tab_b = lista_tabelas[j]

                    # Busca as descrições no JSON original
                    dados_a = next(t for t in tabelas if t["table_name"] == tab_a)
                    dados_b = next(t for t in tabelas if t["table_name"] == tab_b)

                    # Evita duplicar o trabalho se a regra já existir
                    if f"Liga com {tab_b}" in dados_a["description"]:
                        continue

                    print(f"Analisando possível JOIN: {tab_a} + {tab_b} via {coluna}...")
                    
                    try:
                        resposta = chain.invoke({
                            "tabela_a": tab_a, "desc_a": dados_a["description"][:100],
                            "tabela_b": tab_b, "desc_b": dados_b["description"][:100],
                            "coluna": coluna
                        }).strip()

                        if "REGRAS DE JOIN:" in resposta:
                            # Injeta na Tabela A
                            dados_a["description"] += f" {resposta}"
                            modificacoes += 1
                            print(f"  -> Regra adicionada: {resposta}")
                    except Exception as e:
                        print(f"Erro na IA: {e}")

    # Passo 3: Salvar o JSON enriquecido
    if modificacoes > 0:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tabelas, f, indent=2, ensure_ascii=False)
        print(f"\nFinalizado! {modificacoes} novas regras de JOIN foram mapeadas e injetadas no seu dicionário.")
    else:
        print("\nNenhuma regra nova precisou ser adicionada.")

if __name__ == "__main__":
    mapear_relacionamentos()