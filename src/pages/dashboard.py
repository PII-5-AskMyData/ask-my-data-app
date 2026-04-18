"""
dashboard.py — Página principal do Ask My Data com 3 seções:
  1. Consulta SQL (RAG + gráficos)
  2. Guia SQL (exemplos em português)
  3. Schema Preview (tabelas e tipos)
"""
import streamlit as st
import pandas as pd
from src.styles import get_global_css
from src.rag import process_user_query  # get_schema_preview, get_schema_dataframe

# TODO
# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
# def _render_sidebar():
#     """Renderiza a sidebar de navegação."""
#     with st.sidebar:
#         st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
#         st.markdown(
#             "<div class='title-gradient' style='font-size: 1.6rem; margin-bottom: 4px;'>Ask My Data</div>",
#             unsafe_allow_html=True,
#         )
#         st.markdown(
#             "<div style='color: #475569; font-size: 0.8rem; margin-bottom: 30px;'>Plataforma de Inteligência SAP</div>",
#             unsafe_allow_html=True,
#         )

#         st.markdown("<div class='section-label'>Navegação</div>", unsafe_allow_html=True)

#         pages = {
#             "consulta": ("", "Consulta SQL"),
#             "guia": ("", "Guia de Queries"),
#             "schema": ("", "Schema do Banco"),
#         }

#         current = st.session_state.get("dashboard_page", "consulta")

#         for key, (icon, label) in pages.items():
#             active_class = "active" if current == key else ""
#             if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
#                 st.session_state["dashboard_page"] = key
#                 st.rerun()

#         st.markdown("<hr>", unsafe_allow_html=True)

#         # Stats rápidas
#         schema = get_schema_preview()
#         total_tables = len(schema)
#         total_fields = sum(len(t["fields"]) for t in schema)

#         c1, c2 = st.columns(2)
#         with c1:
#             st.markdown(
#                 f"<div class='stat-box'><div class='stat-number'>{total_tables}</div>"
#                 f"<div class='stat-label'>Tabelas</div></div>",
#                 unsafe_allow_html=True,
#             )
#         with c2:
#             st.markdown(
#                 f"<div class='stat-box'><div class='stat-number'>{total_fields}</div>"
#                 f"<div class='stat-label'>Colunas</div></div>",
#                 unsafe_allow_html=True,
#             )

#         st.markdown("<hr>", unsafe_allow_html=True)

#         if st.button("Sair", use_container_width=True, type="secondary"):
#             st.session_state["logged_in"] = False
#             st.session_state["dashboard_page"] = "consulta"
#             st.rerun()


# ─────────────────────────────────────────────────────────────
#  SEÇÃO 1: CONSULTA SQL
# ─────────────────────────────────────────────────────────────
def _render_consulta():
    st.markdown(
        "<div class='animate-in'>"
        "<div class='title-gradient'>Consulta Inteligente</div>"
        "<p class='subtitle'>Descreva sua necessidade e a IA gera o script de extração automaticamente</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Card informativo
    st.markdown(
        """
        <div class="glass-card animate-in-delay">
            <strong>Como funciona?</strong><br>
            A IA analisa a intenção da sua pergunta, busca as tabelas mais relevantes no catálogo SAP usando 
            recuperação semântica (RAG) e gera automaticamente o script SQL correspondente. 
            Além disso, um gráfico estimado é produzido para você ter uma prévia do resultado.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Formulário
    with st.form("query_form", clear_on_submit=False):
        st.markdown(
            "<div style='color: #CBD5E1; font-weight: 600; font-size: 1rem; margin-bottom: 10px;'>Descreva seu Insight:</div>",
            unsafe_allow_html=True,
        )
        query = st.text_area(
            "query",
            placeholder="Ex: Quero analisar o volume de produção por planta nos últimos 3 meses...",
            height=130,
            label_visibility="collapsed",
        )
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        col_btn, _ = st.columns([1, 3])
        with col_btn:
            submit = st.form_submit_button("Gerar Script", type="primary", use_container_width=True)

    # Resultados
    if submit:
        if not query.strip():
            st.warning("O campo não pode estar vazio. Descreva a sua necessidade.")
        else:
            with st.spinner("Analisando intenção e buscando catálogo SAP..."):
                result = process_user_query(query)

            st.markdown("<hr>", unsafe_allow_html=True)

            st.markdown(
                "<div class='section-label' style='margin-top: 10px;'>Resultado da Análise</div>",
                unsafe_allow_html=True,
            )

            # ── Tabelas Mapeadas + Script ──
            col_tables, col_script = st.columns([1, 2.2], gap="large")

            with col_tables:
                st.markdown(
                    "<div style='color: #94A3B8; font-weight: 600; font-size: 0.85rem; margin-bottom: 14px;'>TABELAS MAPEADAS</div>",
                    unsafe_allow_html=True,
                )
                if result.get("tables_identified"):
                    for table in result["tables_identified"]:
                        st.markdown(
                            f"""
                            <div class="table-card">
                                <div class="title">{table['name']}</div>
                                <div class="desc">{table['description']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("Nenhuma tabela mapeada para esta consulta.")

            with col_script:
                st.markdown(
                    f"<div style='color: #94A3B8; font-weight: 600; font-size: 0.85rem; margin-bottom: 14px;'>"
                    f"SCRIPT {result['script_type']} GERADO</div>",
                    unsafe_allow_html=True,
                )
                st.code(result["generated_script"], language="sql")

            # ── Gráfico Automático ──
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-label'>Visualização Estimada dos Dados</div>",
                unsafe_allow_html=True,
            )

            # TODO
            # chart = result.get("chart")
            # if chart:
            #     st.markdown(
            #         f"<div style='color: #CBD5E1; font-weight: 600; font-size: 1.05rem; margin-bottom: 6px;'>"
            #         f"📊 {chart['title']}</div>"
            #         f"<div style='color: #475569; font-size: 0.8rem; margin-bottom: 16px;'>"
            #         f"Tipo de gráfico selecionado automaticamente: <b style='color: #60A5FA;'>{chart['chart_type'].upper()}</b></div>",
            #         unsafe_allow_html=True,
            #     )

            #     df = chart["data"]
            #     x_col = chart["x"]
            #     y_col = chart["y"]
            #     ctype = chart["chart_type"]

            #     if ctype == "bar":
            #         st.bar_chart(df, x=x_col, y=y_col, use_container_width=True)
            #     elif ctype == "line":
            #         st.line_chart(df, x=x_col, y=y_col, use_container_width=True)
            #     elif ctype == "area":
            #         st.area_chart(df, x=x_col, y=y_col, use_container_width=True)
            #     else:
            #         st.bar_chart(df, x=x_col, y=y_col, use_container_width=True)

            #     # Mostrar dados brutos em um expander compacto
            #     with st.expander("Ver dados brutos da amostra"):
            #         st.dataframe(df, use_container_width=True, hide_index=True)

# TODO
# ─────────────────────────────────────────────────────────────
#  SEÇÃO 2: GUIA SQL
# ─────────────────────────────────────────────────────────────
# def _render_guia():
#     st.markdown(
#         "<div class='animate-in'>"
#         "<div class='title-gradient'>Guia de Queries SQL</div>"
#         "<p class='subtitle'>Exemplos práticos organizados por área de negócio para orientar suas consultas</p>"
#         "</div>",
#         unsafe_allow_html=True,
#     )

#     st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

#     # ── Exemplos organizados por categoria ──
#     examples = [
#         {
#             "category": "Produção",
#             "title": "Volume de produção por planta",
#             "description": "Retorna a quantidade total produzida agrupada por centro (planta fabril).",
#             "sql": """SELECT 
#     WERKS AS "Centro (Planta)",
#     SUM(MENGE) AS "Volume Total"
# FROM MSEG 
# WHERE MJAHR = 2026
# GROUP BY WERKS
# ORDER BY "Volume Total" DESC;""",
#         },
#         {
#             "category": "Produção",
#             "title": "Ordens de produção por período",
#             "description": "Lista as ordens de fabricação com data de início e conclusão dentro de um período.",
#             "sql": """SELECT 
#     AUFNR AS "Ordem",
#     GSTRP AS "Início",
#     GLTRP AS "Conclusão",
#     GAMNG AS "Quantidade Planejada",
#     GMEIN AS "Unidade"
# FROM AFKO
# WHERE GSTRP BETWEEN '2026-01-01' AND '2026-03-31'
# ORDER BY GSTRP;""",
#         },
#         {
#             "category": "Faturamento",
#             "title": "Faturamento por organização de vendas",
#             "description": "Soma o valor líquido de notas fiscais agrupado por organização de vendas e moeda.",
#             "sql": """SELECT 
#     VKORG AS "Org. Vendas",
#     WAERK AS "Moeda",
#     SUM(NETWR) AS "Faturamento Total"
# FROM VBRK
# WHERE FKDAT >= DATEADD(MONTH, -6, GETDATE())
# GROUP BY VKORG, WAERK
# ORDER BY "Faturamento Total" DESC;""",
#         },
#         {
#             "category": "Faturamento",
#             "title": "Tipos de faturamento mais frequentes",
#             "description": "Conta a quantidade de documentos por tipo de faturamento.",
#             "sql": """SELECT 
#     FKART AS "Tipo Faturamento",
#     COUNT(*) AS "Quantidade"
# FROM VBRK
# GROUP BY FKART
# ORDER BY "Quantidade" DESC;""",
#         },
#         {
#             "category": "Compras",
#             "title": "Maiores itens de compra por valor",
#             "description": "Identifica os materiais com maior valor total de compra.",
#             "sql": """SELECT 
#     MATNR AS "Material",
#     TXZ01 AS "Descrição",
#     SUM(MENGE * NETPR) AS "Valor Total"
# FROM EKPO
# GROUP BY MATNR, TXZ01
# ORDER BY "Valor Total" DESC;""",
#         },
#         {
#             "category": "Compras",
#             "title": "Preço médio de compra por material",
#             "description": "Calcula o preço médio unitário por material comprado.",
#             "sql": """SELECT 
#     MATNR AS "Material",
#     TXZ01 AS "Descrição",
#     COUNT(*) AS "Qtd Pedidos",
#     AVG(NETPR) AS "Preço Médio"
# FROM EKPO
# GROUP BY MATNR, TXZ01
# HAVING COUNT(*) > 1
# ORDER BY "Preço Médio" DESC;""",
#         },
#         {
#             "category": "Logística",
#             "title": "Entregas por cliente",
#             "description": "Lista as entregas com data e peso agrupados por cliente.",
#             "sql": """SELECT 
#     KUNNR AS "Cliente",
#     COUNT(VBELN) AS "Total Entregas",
#     SUM(BTGEW) AS "Peso Bruto Total"
# FROM LIKP
# WHERE LFDAT >= '2026-01-01'
# GROUP BY KUNNR
# ORDER BY "Total Entregas" DESC;""",
#         },
#         {
#             "category": "Materiais",
#             "title": "Catálogo de materiais por tipo",
#             "description": "Exibe o total de materiais cadastrados por tipo e grupo de mercadorias.",
#             "sql": """SELECT 
#     MTART AS "Tipo Material",
#     MATKL AS "Grupo Mercadorias",
#     COUNT(*) AS "Total"
# FROM MARA
# GROUP BY MTART, MATKL
# ORDER BY "Total" DESC;""",
#         },
#     ]

#     # Agrupar por categoria
#     categories = {}
#     for ex in examples:
#         cat = ex["category"]
#         if cat not in categories:
#             categories[cat] = []
#         categories[cat].append(ex)

#     # Abas por categoria
#     tabs = st.tabs(list(categories.keys()))

#     for tab, (cat_name, cat_examples) in zip(tabs, categories.items()):
#         with tab:
#             for ex in cat_examples:
#                 st.markdown(
#                     f"""
#                     <div class="guide-card">
#                         <div class="tag">{ex['category']}</div>
#                         <div class="gtitle">{ex['title']}</div>
#                         <div class="gdesc">{ex['description']}</div>
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )
#                 st.code(ex["sql"], language="sql")
#                 st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# TODO
# # ─────────────────────────────────────────────────────────────
# #  SEÇÃO 3: SCHEMA PREVIEW
# # ─────────────────────────────────────────────────────────────
# def _render_schema():
#     st.markdown(
#         "<div class='animate-in'>"
#         "<div class='title-gradient'>Schema do Banco de Dados</div>"
#         "<p class='subtitle'>Estrutura completa das tabelas SAP disponíveis no catálogo de dados</p>"
#         "</div>",
#         unsafe_allow_html=True,
#     )

#     st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

#     schema = get_schema_preview()

#     # ── Cards por tabela ──
#     for table in schema:
#         with st.expander(f"📋  {table['table_name']}  —  {table['description']}", expanded=False):
#             # Montar o DataFrame das colunas
#             rows = []
#             for field in table["fields"]:
#                 rows.append(
#                     {
#                         "Coluna": field["name"],
#                         "Tipo": field.get("type", "N/A"),
#                         "Descrição": field["description"],
#                     }
#                 )
#             df = pd.DataFrame(rows)
#             st.dataframe(
#                 df,
#                 use_container_width=True,
#                 hide_index=True,
#                 column_config={
#                     "Coluna": st.column_config.TextColumn("Coluna", width="medium"),
#                     "Tipo": st.column_config.TextColumn("Tipo", width="small"),
#                     "Descrição": st.column_config.TextColumn("Descrição", width="large"),
#                 },
#             )

#     st.markdown("<hr>", unsafe_allow_html=True)

#     # ── Visão consolidada ──
#     st.markdown(
#         "<div class='section-label'>Visão Consolidada (todas as colunas)</div>",
#         unsafe_allow_html=True,
#     )

#     full_df = get_schema_dataframe()

#     # Filtro de tabela
#     selected_table = st.selectbox(
#         "Filtrar por tabela:",
#         options=["Todas"] + sorted(full_df["Tabela"].unique().tolist()),
#     )

#     if selected_table != "Todas":
#         full_df = full_df[full_df["Tabela"] == selected_table]

#     st.dataframe(full_df, use_container_width=True, hide_index=True, height=400)

#     st.markdown(
#         f"<div style='color: #475569; font-size: 0.8rem; margin-top: 8px;'>"
#         f"Exibindo {len(full_df)} colunas de {full_df['Tabela'].nunique()} tabela(s).</div>",
#         unsafe_allow_html=True,
#     )

# TODO
# # ─────────────────────────────────────────────────────────────
# #  RENDERIZADOR PRINCIPAL
# # ─────────────────────────────────────────────────────────────
def render():
    """Ponto de entrada do dashboard: injeta CSS, sidebar e renderiza a seção selecionada."""
    st.markdown(get_global_css(), unsafe_allow_html=True)
    # _render_sidebar()

    page = st.session_state.get("dashboard_page", "consulta")

    if page == "consulta":
        _render_consulta()
    # elif page == "guia":
    #     # _render_guia()
    # elif page == "schema":
    #     # _render_schema()
